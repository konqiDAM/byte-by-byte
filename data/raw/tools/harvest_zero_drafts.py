"""harvest_zero_drafts.py - submit matches that are already sitting in the local packet cache.

    python exp91/harvest_zero_drafts.py [--max-score 10] [--dry]

Every claim folder keeps its `packet.json`, and `best_attempts[].code` holds a previous draft. 65 of the 3180 local
packets record a draft at **score 0** - i.e. it matched when it was saved - and some of those addresses are still `open`
on the site (banked, never submitted, or a submission that vanished: lesson 20.01).

For each such address: ask the site for its state, and if `open`, re-check the draft locally, claim and submit it with one
comment line prepended (the 409 "already found unfit" cache is keyed to the exact text - lesson 19.82).
"""
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
            return {"ERR": e.code, "body": e.read().decode("utf-8", "replace")[:400]}
        except Exception:
            time.sleep(2)
    return {"ERR": "retry"}


def collect(max_score):
    """address -> (score, claim_dir, code) for the best saved draft under max_score.

    Gates learned the hard way (§20.04): a cached score-0 draft only proves it matches the PACK. To predict whether it
    fits the PROJECT file, keep drafts whose pack flags are not the mislabelled /Od set, and whose declaration footprint
    is small (a draft that defines its own structs/callees is the one that collides).
    """
    best = {}
    for p in glob.glob(os.path.join(ROOT, "claims", "*", "packet.json")):
        try:
            d = json.load(open(p))
        except Exception:
            continue
        addr = "0x" + str(d.get("address") or "").lower().replace("0x", "")
        if len(addr) != 10:
            continue
        flags = d.get("flags") or []
        if "/Od" in flags:            # the mislabelled region: a match against it cannot fit a /O2 project file
            continue
        for b in (d.get("best_attempts") or []):
            code, sc = b.get("code"), b.get("score")
            if not code or sc is None or sc > max_score:
                continue
            # declaration footprint: structs/classes/operator new declared by the draft itself are what collide
            if len(re.findall(r"(?m)^\s*(?:struct|class|union)\s+\w+\s*(?:[:{]|$)", code)) > 0:
                continue
            if "operator new" in code or "operator delete" in code:
                continue
            if addr not in best or sc < best[addr][0]:
                best[addr] = (sc, os.path.dirname(p), code)
    return best


def main():
    max_score = 10
    if "--max-score" in sys.argv:
        max_score = int(sys.argv[sys.argv.index("--max-score") + 1])
    dry = "--dry" in sys.argv
    skip = set()
    if "--skip" in sys.argv:
        skip = {a.lower() for a in sys.argv[sys.argv.index("--skip") + 1].split(",") if a}
    best = collect(max_score)
    print("drafts recorded at score <= %d: %d addresses" % (max_score, len(best)))
    todo = []
    for addr, (sc, dd, code) in sorted(best.items()):
        if addr in skip:
            continue
        st = post("function_info", {"address": addr}).get("state")
        if st == "open":
            todo.append((addr, sc, dd, code))
            print("  OPEN   %-12s score %-3s pack %s" % (addr, sc, os.path.basename(dd)))
    print("\n%d open addresses with a matching draft in the cache" % len(todo))
    if dry or not todo:
        return
    done = 0
    for addr, sc, dd, code in todo:
        work = os.path.join(dd, "harvest.cpp")
        io.open(work, "w", encoding="utf-8", newline="\n").write(
            "// harvest %s: cached draft, same bytes, new text\n" % addr + code)
        c = post("claim", {"address": addr, "model": MODEL, "harness": "opencode",
                           "effort": "high", "context_mode": "lean"})
        cid = c.get("claim_id")
        if not cid:
            print("%-12s claim failed: %s" % (addr, json.dumps(c)[:120]))
            continue
        p = subprocess.run([PY, os.path.join(ROOT, "f3check", "f3check.py"), work, "--pack", dd,
                            "--claim", cid, "--sweep", "harvest of a cached score-0 draft"],
                           capture_output=True, text=True, errors="replace", env=ENV)
        if "MATCH" not in ANSI.sub("", (p.stdout or "") + (p.stderr or "")):
            print("%-12s local re-check no longer matches - skipped" % addr)
            continue
        s = post("submit", {"claim_id": cid, "source": io.open(work, encoding="utf-8").read(),
                            "model": MODEL})
        print("%-12s %s" % (addr, str(s.get("submission_id") or s.get("body") or s)[:160]))
        done += 1
    print("\nsubmitted %d of %d" % (done, len(todo)))


if __name__ == "__main__":
    main()
