"""rescore_nearmiss.py - re-score cached near-miss drafts under the file's REAL flag sets.

    python exp91/rescore_nearmiss.py [--max-score 50] [--workers 6] [--submit]

The packet cache holds a saved draft for nearly every address we have ever claimed, with the score it was saved at. Those
scores were taken under the pack's DECLARED flags - and the whole /Od-labelled region is really /O2, per file, with /GS or
/GS- varying (lessons 19.90/19.93). So a draft recorded at "score 41" may be a match today under the right set.

For each open address with a cached draft at 0 < score <= max-score, compile it under every candidate set and report the
best. --submit submits any that reach MATCH under a set the pack already declares (a match under a corrected set must go
through the compile_flags route instead - lesson 19.93).
"""
import concurrent.futures as cf
import glob
import io
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

API = "https://f3decomp.com/api/v1/"
KEY = io.open(os.path.expanduser(r"~\.f3decomp_key"), encoding="utf-8").read().strip()
ROOT = r"C:\f3decomp"
PY = r"C:\Users\void\AppData\Local\Programs\Python\Python310\python.exe"
MODEL = "DeepSeek V4.1 Flash"
ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
SETS = [("declared", None),
        ("O2/GS", "/MT,/O2,/GS,/EHsc,/Gy"),
        ("O2/GS-", "/MT,/O2,/GS-,/EHsc,/Gy")]
ENV = dict(os.environ, F3CHECK_IMAGE=r"D:\Fallout3\Fallout3.exe",
           F3CHECK_INDEX=os.path.join(ROOT, "function_index.json"),
           F3CHECK_SYMBOLS=os.path.join(ROOT, "f3decomp_symbols.json"),
           F3CHECK_TOOLS=os.path.join(ROOT, "win_tools"),
           F3_MSVC_ROOT=os.path.join(ROOT, "vs2005"))


def post(path, payload=None):
    r = urllib.request.Request(API + path, data=json.dumps(payload or {}).encode(),
                               headers={"Authorization": "Bearer " + KEY,
                                        "User-Agent": "Mozilla/5.0",
                                        "Content-Type": "application/json"})
    for _ in range(3):
        try:
            return json.loads(urllib.request.urlopen(r).read().decode() or "{}")
        except urllib.error.HTTPError as e:
            return {"ERR": e.code, "body": e.read().decode("utf-8", "replace")[:300]}
        except Exception:
            time.sleep(2)
    return {"ERR": "retry"}


def score(pack, cand, flags):
    cmd = [PY, os.path.join(ROOT, "f3check", "f3check.py"), cand, "--pack", pack,
           "--sweep", "old-try re-score under the file's real flag sets (20.10)"]
    if flags:
        cmd += ["--flags", flags]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, errors="replace", env=ENV, timeout=600)
    except subprocess.TimeoutExpired:
        return "timeout"
    out = ANSI.sub("", (p.stdout or "") + (p.stderr or ""))
    if "MATCH" in out:
        return "MATCH"
    # f3check only prints an "N instructions differ" line when work notes are enabled; count the diff pairs instead
    n = len(re.findall(r"(?m)^ORIG ", out))
    if n:
        return n
    m = re.search(r"(\d+)\s+instructions? differ", out) or re.search(r"ndiff[= ]+(\d+)", out)
    if m:
        return int(m.group(1))
    return "?"


def collect(max_score):
    best = {}
    for p in glob.glob(os.path.join(ROOT, "claims", "*", "packet.json")):
        try:
            d = json.load(open(p))
        except Exception:
            continue
        addr = "0x" + str(d.get("address") or "").lower().replace("0x", "")
        if len(addr) != 10:
            continue
        for b in (d.get("best_attempts") or []):
            code, sc = b.get("code"), b.get("score")
            if not code or sc is None or sc == 0 or sc > max_score:
                continue
            if addr not in best or sc < best[addr][0]:
                best[addr] = (sc, os.path.dirname(p), code)
    return best


def one(item):
    addr, sc, dd, code = item
    work = os.path.join(dd, "rescore.cpp")
    io.open(work, "w", encoding="utf-8", newline="\n").write(
        "// old-try re-score %s\n" % addr + code)
    res = {}
    for name, flags in SETS:
        res[name] = score(dd, work, flags)
        if res[name] == "MATCH":
            break
    return addr, sc, dd, res


def main():
    max_score = int(sys.argv[sys.argv.index("--max-score") + 1]) if "--max-score" in sys.argv else 50
    workers = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 6
    cands = collect(max_score)
    print("cached near-miss drafts (0 < score <= %d): %d addresses" % (max_score, len(cands)))
    todo = []
    for addr, (sc, dd, code) in sorted(cands.items()):
        if post("function_info", {"address": addr}).get("state") == "open":
            todo.append((addr, sc, dd, code))
    print("of which still open on the site: %d\n" % len(todo))
    wins = []
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        for addr, sc, dd, res in ex.map(one, todo):
            best = min([v for v in res.values() if isinstance(v, int)] or [999])
            tag = ""
            if res.get("declared") == "MATCH":
                tag = "  <-- MATCH under the DECLARED set (submittable)"
            elif "MATCH" in res.values():
                tag = "  <-- MATCH under a CORRECTED set (compile_flags route)"
            elif best < sc:
                tag = "  <-- better than the recorded %s" % sc
            print("%-12s recorded %-4s declared %-6s O2/GS %-6s O2/GS- %-6s%s"
                  % (addr, sc, res.get("declared"), res.get("O2/GS"), res.get("O2/GS-"), tag))
            if "MATCH" in res.values():
                wins.append({"address": addr, "recorded": sc, "pack": dd,
                             "sets": {k: v for k, v in res.items() if v == "MATCH"}})
    io.open(os.path.join(ROOT, "out", "_old_try_wins.json"), "w", encoding="utf-8",
            newline="\n").write(json.dumps(wins, indent=1))
    print("\nmatches found among old tries: %d (out/_old_try_wins.json)" % len(wins))


if __name__ == "__main__":
    main()
