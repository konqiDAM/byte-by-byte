"""triage_twins.py - decide whether a claimed twin is a good option, from its packet.

    python exp91/triage_twins.py <claim_id> [<claim_id> ...]

Prints, per claim: size, flags, whether /O2 is in accept_also, the best saved attempt score, the number of give-ups that
are PROCESS failures rather than attempts ("check refused", "missing notes", "no plan"), and the newest substantive
give-up reason. That is everything needed to judge "is this a wall or a farmed count".
"""
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

API = "https://f3decomp.com/api/v1/"
KEY = io.open(os.path.expanduser(r"~\.f3decomp_key"), encoding="utf-8").read().strip()

PROCESS = re.compile(r"check refused|missing notes|no plan|random pick|screening|no work done", re.I)


def post(path, payload=None):
    r = urllib.request.Request(API + path, data=json.dumps(payload or {}).encode(),
                               headers={"Authorization": "Bearer " + KEY,
                                        "User-Agent": "Mozilla/5.0",
                                        "Content-Type": "application/json"})
    for _ in range(3):
        try:
            return json.loads(urllib.request.urlopen(r).read().decode() or "{}")
        except urllib.error.HTTPError as e:
            return {"ERR": e.code, "body": e.read().decode("utf-8", "replace")[:200]}
        except Exception:
            time.sleep(2)
    return {"ERR": "retry"}


def main():
    for cid in sys.argv[1:]:
        p = post("packet", {"claim_id": cid, "context_mode": "resume"})
        if p.get("ERR"):
            print("%s  ERR %s" % (cid, p))
            continue
        hist = p.get("history") or {}
        reasons = [r for r in (hist.get("recent_give_up_reasons") or [])]
        proc = sum(1 for r in reasons if PROCESS.search(str(r)))
        bs = p.get("best_attempts") or []
        best = [(b.get("score"), (b.get("reason") or "")[:60]) for b in bs]
        flags = p.get("flags") or []
        acc = p.get("accept_also") or []
        print("=== %s  %-12s %-5s" % (cid, p.get("address"), p.get("size")))
        print("    flags %s   accept_also %s   -> %s" % (
            ",".join(flags), acc or "-",
            "SUBMITTABLE" if (not acc or flags in acc or any(sorted(a) == sorted(flags) for a in acc)) else "flag route"))
        print("    give_ups %s (screening %s)   near_misses %s   checkpoints %s" % (
            hist.get("give_ups"), hist.get("screening_give_ups"), p.get("near_misses"), p.get("checkpoints")))
        print("    recent reasons: %d shown, %d look like PROCESS failures (not attempts)" % (len(reasons), proc))
        for r in reasons[:3]:
            print("       - %s" % str(r)[:150])
        print("    best saved attempt: %s" % (best if best else "none"))
        kf = p.get("known_flags") or []
        for f in kf[:2]:
            print("    known_flag [%s %s]: %s" % (f.get("category"), f.get("status"), str(f.get("note"))[:140]))
        print()


if __name__ == "__main__":
    main()
