"""rescore_flags.py - re-score /Od-labelled candidates under the region's REAL flags.

    python exp91/rescore_flags.py [--limit N] [--apply]

The /Od region's true flags are /MT /O2 /GS- /EHsc /Gy (lessons 19.90). Every candidate written against the declared
/Od /Oy- /GS set was measured in the wrong configuration, so a near miss may be a match. Scores each candidate file
under both sets with f3check --flags (no claim needed) and reports the ones that improve or match.
"""
import glob
import io
import json
import os
import re
import subprocess
import sys

ROOT = r"C:\f3decomp"
PY = r"C:\Users\void\AppData\Local\Programs\Python\Python310\python.exe"
ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
REAL = "/MT,/O2,/GS-,/EHsc,/Gy"
ENV = dict(os.environ, F3CHECK_IMAGE=r"D:\Fallout3\Fallout3.exe",
           F3CHECK_INDEX=os.path.join(ROOT, "function_index.json"),
           F3CHECK_SYMBOLS=os.path.join(ROOT, "f3decomp_symbols.json"),
           F3CHECK_TOOLS=os.path.join(ROOT, "win_tools"),
           F3_MSVC_ROOT=os.path.join(ROOT, "vs2005"))


def score(pack, cand, flags=None):
    cmd = [PY, os.path.join(ROOT, "f3check", "f3check.py"), cand, "--pack", pack,
           "--why", "re-score under corrected region flags (19.90)", "--sweep",
           "declared vs /MT,/O2,/GS-,/EHsc,/Gy"]
    if flags:
        cmd += ["--flags", flags]
    p = subprocess.run(cmd, capture_output=True, text=True, errors="replace", env=ENV, timeout=600)
    out = ANSI.sub("", (p.stdout or "") + (p.stderr or ""))
    if "MATCH" in out:
        return "MATCH", None
    m = re.search(r"(\d+)\s+instructions? differ", out) or re.search(r"ndiff[= ]+(\d+)", out)
    return "wip", (int(m.group(1)) if m else None)


def main():
    limit = None
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])
    rows = []
    seen = set()
    for pj in glob.glob(os.path.join(ROOT, "claims", "*", "pack.json")):
        try:
            d = json.load(open(pj))
        except Exception:
            continue
        flags = d.get("flags") or []
        if "/Od" not in flags:
            continue
        addr = "0x" + str(d.get("address", "")).lower().replace("0x", "")
        if addr in seen or addr in ("0x", "0x"):
            continue
        dd = os.path.dirname(pj)
        cands = [f for f in glob.glob(os.path.join(dd, "*.cpp"))
                 if not os.path.basename(f).startswith(("unit_", "tu_"))]
        if not cands:
            continue
        cand = max(cands, key=os.path.getsize)          # the most-developed draft
        seen.add(addr)
        rows.append((addr, d.get("size"), dd, cand))
    rows.sort(key=lambda r: (r[1] or 0))
    if limit:
        rows = rows[:limit]
    print("%d /Od-labelled addresses with a candidate on disk\n" % len(rows))
    impro = []
    for addr, size, dd, cand in rows:
        a_verdict, a_n = score(dd, cand)                       # declared flags
        b_verdict, b_n = score(dd, cand, REAL)                 # corrected flags
        tag = ""
        if b_verdict == "MATCH" and a_verdict != "MATCH":
            tag = "  <-- MATCH under the real flags"
        elif a_n is not None and b_n is not None and b_n < a_n:
            tag = "  <-- better"
        if tag:
            impro.append((addr, size, os.path.basename(cand), a_n, b_n, dd))
        print("%-12s %-5s %-26s declared %-5s real %-5s%s"
              % (addr, size, os.path.basename(cand), a_n if a_n is not None else a_verdict,
                 b_n if b_n is not None else b_verdict, tag))
    io.open(os.path.join(ROOT, "out", "_rescore_flags.json"), "w", encoding="utf-8",
            newline="\n").write(json.dumps(impro, indent=1))
    print("\nimproved or matched: %d (written to out/_rescore_flags.json)" % len(impro))


if __name__ == "__main__":
    main()
