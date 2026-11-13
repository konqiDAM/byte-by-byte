"""Re-probe functions we already hold, looking for code uploaded since we looked.

    python exp91\\rivals_delta.py [--limit 300] [--out rivals\\_delta.txt]

We harvest a function once and never look again, so a better attempt someone uploaded
afterwards is invisible to us. This ranks the addresses worth re-reading - the ones where a
newer draft would actually change our position - and prints the list the harvester can take
with `--addresses`.

Ranking: a close draft first (ndiff <= 10: any improvement there is a near-miss or a match),
then the functions other people are still working (give_ups, then near_misses), because that
is where new checkpoints appear. Cost is ~5 requests per address.
"""
import argparse
import glob
import json
import os
import sys

sys.path.insert(0, os.path.join(r"C:\f3decomp", "exp91"))
import rivals_import as R  # noqa: E402

BANDS = ["<=255", "256-511", "512-1K", "1K-4K", "4K+"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=300)
    ap.add_argument("--budget", type=int, default=3000)
    ap.add_argument("--out", default=os.path.join(R.RIVALS, "_delta.txt"))
    args = ap.parse_args()

    api = R.Api(args.budget)
    pool = {}
    for band in BANDS:
        r = api.post("list_functions", {"band": band, "order": "give_ups",
                                        "max_give_ups": 9999, "limit": 500})
        for f in r.get("functions") or []:
            pool[f["address"].lower()] = {"gu": f.get("give_ups") or 0,
                                          "nm": f.get("near_misses") or 0,
                                          "size": f.get("size") or 0}
    print("pool now: %d functions (%d requests)" % (len(pool), api.used))

    rows = []
    for p in glob.glob(os.path.join(R.RIVALS, "0x*", "index.json")):
        d = R.load(p, {})
        a = (d.get("address") or os.path.basename(os.path.dirname(p))).lower()
        if a not in pool:                 # gone from the pool: matched, closed, or claimed
            continue
        b = d.get("best") or {}
        rows.append({"addr": a, "ndiff": b.get("ndiff"), "size": pool[a]["size"],
                     "gu": pool[a]["gu"], "nm": pool[a]["nm"],
                     "lane": d.get("lane") or "-",
                     "twin": bool(d.get("twin_fnv") or d.get("twin_unit_file"))})
    print("of those, we already hold %d" % len(rows))

    close = [r for r in rows if r["ndiff"] is not None and r["ndiff"] <= 10]
    hot = [r for r in rows if r not in close]
    close.sort(key=lambda r: (r["ndiff"], -r["gu"], r["size"]))
    hot.sort(key=lambda r: (-r["gu"], -r["nm"], r["ndiff"] if r["ndiff"] is not None else 9999))
    picked = (close + hot)[:args.limit]

    print("\nclose drafts (ndiff <= 10) still in the pool: %d" % len(close))
    print("heavily-attempted remainder: %d" % len(hot))
    print("picked: %d  (~%d requests)" % (len(picked), len(picked) * 5))
    print("\ntop 20:")
    print("%-12s %5s %6s %4s %4s %5s %s" % ("address", "ndiff", "size", "gu", "nm", "twin", "lane"))
    for r in picked[:20]:
        print("%-12s %5s %6d %4d %4d %5s %s"
              % (r["addr"], "-" if r["ndiff"] is None else r["ndiff"], r["size"],
                 r["gu"], r["nm"], "yes" if r["twin"] else "-", r["lane"]))
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(",".join(r["addr"] for r in picked) + "\n")
    print("\nwrote %s (%d addresses, pass with --addresses)" % (args.out, len(picked)))


if __name__ == "__main__":
    main()
