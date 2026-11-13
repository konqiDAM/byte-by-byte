"""Score every downloaded-but-unscored rival draft, without touching the API.

    python exp91\\score_pending.py [--jobs 24]

The harvester only scores at the end of a run, so a run that is still probing (or one that
crashed) leaves drafts sitting in rivals\\_incoming with no ndiff. This scores those now,
in parallel, using each pack already on disk. 0 API requests.
"""
import argparse
import glob
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.join(r"C:\f3decomp", "exp91"))
import rivals_import as R  # noqa: E402


def pending(info):
    return [c for c in info.get("checkpoints") or []
            if c.get("tmp") and os.path.isfile(c["tmp"]) and c.get("ndiff") is None]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int,
                    default=max(2, min(24, (os.cpu_count() or 8) - 2)))
    args = ap.parse_args()

    packs = R.pack_map()
    seen = R.load(R.SEEN, {})
    todo = {}
    for p in glob.glob(os.path.join(R.RIVALS, "0x*", "index.json")):
        info = json.load(open(p, encoding="utf-8"))
        pend = pending(info)
        if pend:
            todo[info.get("address") or os.path.basename(os.path.dirname(p))] = info
    files = sum(len(pending(i)) for i in todo.values())
    print("%d addresses, %d unscored files, %d workers" % (len(todo), files, args.jobs))
    if not todo:
        return
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as ex:
        list(ex.map(lambda kv: R.finalize(kv[0], kv[1], packs, 1, seen), todo.items()))
    R.save(R.SEEN, seen)
    infos = R.scan_infos()
    R.save(R.INDEX, infos)
    R.write_report(infos)
    R.write_structures()
    usable = sum(1 for i in infos.values()
                 if (i.get("best") or {}).get("ndiff") is not None
                 and not (i.get("best") or {}).get("errs")
                 and (i.get("best") or {}).get("extent") == i.get("size"))
    print("done: %d scored addresses, %d usable" % (len(infos), usable))


if __name__ == "__main__":
    main()
