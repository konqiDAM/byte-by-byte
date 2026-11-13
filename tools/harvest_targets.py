"""harvest_targets.py - where the harvest should go next, measured.

    python exp91/harvest_targets.py

Joins three things:
  * the pending pool (what is still open), by lane and by address prefix
  * the harvest (what has been fetched), by lane and prefix
  * the yield (usable drafts, ndiff<=2), by lane and prefix
so the harvester can be told which sections to spend on and which to skip.
"""
import glob
import json
import os
from collections import defaultdict

ROOT = r"C:\f3decomp"

LANES = [(255, "tiny"), (512, "s256"), (1024, "s512"), (1 << 20, "s1k")]

# address ranges that cannot be won - do not spend harvest on them
DEAD = [
    (0x00BA0000, 0x00C00000, "speedtree: EH catch-funclet index class (the span ends at the funclets)"),
    (0x00BF0000, 0x00C40000, "CRT: detached SEH funclets / index fragments, not standalone functions"),
    (0x00C00000, 0x00C40000, "script/CRT fragments (same)"),
]


def lane(sz):
    for lim, name in LANES:
        if sz <= lim:
            return name
    return "s1k"


def dead(a):
    for lo, hi, why in DEAD:
        if lo <= a < hi:
            return why
    return None


def main():
    pool = json.load(open(os.path.join(ROOT, "exp91", "pool_now.json"), encoding="utf-8"))
    done = {os.path.basename(s)[6:-4].lower() for s in glob.glob(os.path.join(ROOT, "claims", "match_*.cpp"))}
    pend = {}
    for a, f in pool.items():
        k = a.lower().replace("0x", "")
        if k in done:
            continue
        pend[k] = f.get("size") or 0

    harv = {}
    for d in glob.glob(os.path.join(ROOT, "rivals", "0x*")):
        a = os.path.basename(d).lower().replace("0x", "")
        j = {}
        try:
            j = json.load(open(os.path.join(d, "index.json"), encoding="utf-8"))
        except Exception:
            pass
        b = j.get("best") or {}
        size = j.get("size") or pend.get(a) or 0
        usable = (b.get("ndiff") is not None and b.get("extent") == size and not (b.get("errs") or 0))
        harv[a] = dict(size=size, ndiff=b.get("ndiff"), usable=usable)

    print("pending pool: %d   harvested: %d   both: %d"
          % (len(pend), len(harv), len(set(pend) & set(harv))))

    print("\n=== by lane ===")
    print("%-6s %8s %10s %10s %9s %9s" % ("lane", "pending", "harvested", "unharv", "usable", "ndiff<=2"))
    for lim, name in LANES:
        p = [a for a, s in pend.items() if lane(s) == name]
        h = [a for a in p if a in harv]
        u = [a for a in h if harv[a]["usable"]]
        n2 = [a for a in h if harv[a]["ndiff"] is not None and harv[a]["ndiff"] <= 2]
        print("%-6s %8d %10d %10d %9d %9d" % (name, len(p), len(h), len(p) - len(h), len(u), len(n2)))

    print("\n=== by address prefix (high 16 bits), best yield first ===")
    pre = defaultdict(lambda: dict(p=0, h=0, u=0, n1=0))
    for a, s in pend.items():
        pre[a[:4]]["p"] += 1
    for a, v in harv.items():
        e = pre[a[:4]]
        e["h"] += 1
        if v["usable"]:
            e["u"] += 1
        if v["ndiff"] is not None and v["ndiff"] <= 1:
            e["n1"] += 1
    rows = [(k, v) for k, v in pre.items() if v["h"] >= 4]
    rows.sort(key=lambda kv: (-kv[1]["u"], -kv[1]["n1"]))
    print("%-8s %8s %8s %7s %6s  %s" % ("prefix", "pending", "harv", "usable", "nd1", "dead?"))
    for k, v in rows:
        lo = int(k, 16) << 16
        d = dead(lo)
        print("0x%sxx %8d %8d %7d %6d  %s" % (k, v["p"], v["h"], v["u"], v["n1"], (d[:28] if d else "")))

    print("\n=== the dead ranges in the pending pool ===")
    for lo, hi, why in DEAD:
        sub = [a for a, s in pend.items() if lo <= int(a, 16) < hi]
        print("  0x%08x-0x%08x  %4d pending  %s" % (lo, hi, len(sub), why))

    print("\n=== unharvested, alive, by lane (the actual target list) ===")
    for lim, name in LANES:
        t = [a for a, s in pend.items() if lane(s) == name and a not in harv and not dead(int(a, 16))]
        print("  %-6s %4d functions  %.0f KB" % (name, len(t), sum(pend[a] for a in t) / 1024.0))


if __name__ == "__main__":
    main()
