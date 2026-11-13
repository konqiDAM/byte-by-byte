"""Map of what is still missing in the harvest: per band, per bucket, what is left.

    python exp91\harvest_map.py [out.md]

Queries the pool (functions other contributors gave up on), compares it with what the
harvester has already visited (rivals\\_log.jsonl) and what it holds (rivals\<addr>), and
writes the map: per band, how many functions exist, how many are done, how many are left,
and how many of the left ones carry a near miss (the ones whose code is most likely to be
worth taking).
"""
import json
import os
import sys
import urllib.request
from collections import Counter
from datetime import datetime, timezone

API = "https://f3decomp.com/api/v1/"
ROOT = r"C:\f3decomp"
RIVALS = os.path.join(ROOT, "rivals")
BANDS = ["<=255", "256-511", "512-1K", "1K-4K", "4K+"]


def key():
    return open(os.path.join(os.environ["USERPROFILE"], ".f3decomp_key")).read().strip()


def post(path, body):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode(),
                                 headers={"Authorization": "Bearer " + key(),
                                          "User-Agent": "Mozilla/5.0",
                                          "Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=180).read().decode() or "{}")


def swept():
    """addresses the harvester has already visited"""
    path = os.path.join(RIVALS, "_log.jsonl")
    out = set()
    if os.path.isfile(path):
        for line in open(path, encoding="utf-8"):
            r = json.loads(line)
            if r.get("event") == "fetch":
                out.add(r["address"].lower())
    return out


def held():
    """address -> what we hold for it: ndiff, whether it is usable, which lane took it"""
    out = {}
    import glob
    for p in glob.glob(os.path.join(RIVALS, "0x*", "index.json")):
        d = json.load(open(p, encoding="utf-8"))
        a = (d.get("address") or os.path.basename(os.path.dirname(p))).lower()
        b = d.get("best") or {}
        size, ext = d.get("size") or 0, b.get("extent") or 0
        out[a] = {"ndiff": b.get("ndiff"), "lane": d.get("lane") or "-",
                  "usable": bool(size and ext == size and (b.get("errs") or 0) == 0)}
    return out


def main():
    done = swept()
    have = held()
    rows = []
    for band in BANDS:
        r = post("list_functions", {"band": band, "order": "give_ups", "max_give_ups": 9999,
                                    "limit": 500})
        for f in r.get("functions") or []:
            a = f["address"].lower()
            rows.append(dict(band=band, addr=a, size=f.get("size") or 0,
                             gu=f.get("give_ups") or 0, nm=f.get("near_misses") or 0,
                             ec=f.get("earlier_claims") or 0,
                             flag=(f.get("flagged") or {}).get("state") or "",
                             swept=a in done,
                             ndiff=(have.get(a) or {}).get("ndiff"),
                             usable=(have.get(a) or {}).get("usable", False),
                             lane=(have.get(a) or {}).get("lane") or "-"))
    # buckets
    gave_up = [r for r in rows if r["gu"] >= 1]
    claimed_only = [r for r in rows if r["gu"] == 0 and r["ec"] >= 1]
    never = [r for r in rows if r["gu"] == 0 and r["ec"] == 0]

    lines = ["# Harvest map - %s" % datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), "",
             "What the harvest has taken and what is still out there.", "",
             "| band | pool (gave up) | swept | left | left with a near miss | left, never claimed |",
             "|---|---|---|---|---|---|"]
    for band in BANDS:
        b = [r for r in gave_up if r["band"] == band]
        left = [r for r in b if not r["swept"]]
        lines.append("| %s | %d | %d | %d | %d | %d |"
                     % (band, len(b), len(b) - len(left), len(left),
                        len([r for r in left if r["nm"] >= 1]),
                        len([r for r in b if r["ec"] == 0])))
    total_left = len([r for r in gave_up if not r["swept"]])
    nm_left = len([r for r in gave_up if not r["swept"] and r["nm"] >= 1])
    lines += ["", "## Totals", "",
              "- functions others gave up on: **%d**" % len(gave_up),
              "- swept so far: **%d** (%.0f%%)" % (len(gave_up) - total_left,
                                                   100.0 * (len(gave_up) - total_left) / max(1, len(gave_up))),
              "- **still missing: %d**, of which **%d carry a near miss** (their code is the most likely to be takeable)"
              % (total_left, nm_left),
              "- claimed by someone but never given up: %d (their checkpoints may still exist - not in the pool filter)"
              % len(claimed_only),
              "- never claimed by anyone: %d (nothing to harvest - no code exists)" % len(never),
              "- functions we hold a scored candidate for: %d, of which **%d are usable** (compile clean, size exact)"
              % (len([r for r in rows if r["ndiff"] is not None]),
                 len([r for r in rows if r["usable"]])),
              "",
              "## Yield so far", ""]
    swept_rows = [r for r in gave_up if r["swept"]]
    lines += ["- of the %d swept, %d had rival code at all, %d gave a scored candidate, %d are usable"
              % (len(swept_rows), len([r for r in swept_rows if r["nm"] >= 1]),
                 len([r for r in swept_rows if r["ndiff"] is not None]),
                 len([r for r in swept_rows if r["usable"]])),
              "- the close ones (ndiff <= 10): %s"
              % ", ".join("`%s` (%s%s)" % (r["addr"], r["ndiff"],
                                           ", usable" if r["usable"] else "")
                          for r in rows if r["ndiff"] is not None and r["ndiff"] <= 10),
              ""]
    by_lane = {}
    for r in rows:
        if r["ndiff"] is None:
            continue
        t = by_lane.setdefault(r["lane"], {"n": 0, "usable": 0, "best": None})
        t["n"] += 1
        t["usable"] += 1 if r["usable"] else 0
        if t["best"] is None or r["ndiff"] < t["best"]:
            t["best"] = r["ndiff"]
    if by_lane:
        lines += ["## Which lane paid", "",
                  "| lane | scored | usable | best ndiff |", "|---|---|---|---|"]
        for name in sorted(by_lane):
            t = by_lane[name]
            lines.append("| %s | %d | %d | %s |" % (name, t["n"], t["usable"], t["best"]))
        lines.append("")
    lines += ["## The missing ones, by band (near misses first)", ""]
    for band in BANDS:
        left = [r for r in gave_up if r["band"] == band and not r["swept"]]
        left.sort(key=lambda r: (-r["nm"], -r["gu"]))
        if not left:
            continue
        lines += ["### %s - %d left" % (band, len(left)), "",
                  "| address | size | give-ups | near misses | earlier claims | flagged |",
                  "|---|---|---|---|---|---|"]
        for r in left[:40]:
            lines.append("| `%s` | %s | %s | %s | %s | %s |"
                         % (r["addr"], r["size"], r["gu"], r["nm"], r["ec"], r["flag"] or "-"))
        if len(left) > 40:
            lines.append("| ... %d more | | | | | |" % (len(left) - 40))
        lines.append("")
    out = "\n".join(lines) + "\n"
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(RIVALS, "_harvest_map.md")
    open(path, "w", encoding="utf-8", newline="\n").write(out)
    print(out[:2000])
    print("\nwritten %s" % path)


if __name__ == "__main__":
    main()
