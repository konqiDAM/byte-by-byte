"""Fetch the current pool metadata and cross it with the local shape indexes - cheap.

3-5 requests total (list_bands + one list_functions per band), and then everything is offline:
the trivial shapes come from exp91/simple_shapes.json (a LOCAL scan of the image) and the
twins come from twins/cache/twins.json.

    python exp91/pool_now.py            # fetch + save
    python exp91/pool_now.py --cross    # cross the saved pool with the local indexes
"""
import json
import os
import sys

sys.path.insert(0, r"C:\f3decomp\tools")
sys.path.insert(0, r"C:\f3decomp\exp91")
import q  # noqa: E402

ROOT = r"C:\f3decomp"
POOL = os.path.join(ROOT, "exp91", "pool_now.json")
SHAPES = os.path.join(ROOT, "exp91", "simple_shapes.json")
TWINS = r"C:\f3decomp\twins\cache\twins.json"


def post(path, payload=None):
    import urllib.request
    key = open(os.path.join(os.environ["USERPROFILE"], ".f3decomp_key")).read().strip()
    req = urllib.request.Request(
        "https://f3decomp.com/api/v1/" + path, data=json.dumps(payload or {}).encode(),
        headers={"Authorization": "Bearer " + key, "User-Agent": "Mozilla/5.0",
                 "Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=60).read().decode() or "{}")


def fetch():
    bands = post("list_bands")
    bl = bands.get("bands") or bands.get("allowed_bands") or []
    names = []
    for b in bl:
        if isinstance(b, dict):
            if b.get("allowed", True):
                names.append(b.get("band") or b.get("name"))
        else:
            names.append(b)
    print("bands:", names)
    pool = {}
    for b in names:
        for order in ("size",):
            r = post("list_functions", {"band": b, "order": order, "limit": 600})
            for f in (r.get("functions") or []):
                pool[f["address"]] = f
    json.dump(pool, open(POOL, "w"), indent=1)
    print("pool entries:", len(pool))
    return pool


def cross():
    pool = json.load(open(POOL, encoding="utf-8"))
    shapes = json.load(open(SHAPES, encoding="utf-8"))
    twins = json.load(open(TWINS, encoding="utf-8")) if os.path.isfile(TWINS) else {}
    submitted = set()
    for f in os.listdir(os.path.join(ROOT, "claims")):
        if f.startswith("match_") and f.endswith(".cpp"):
            submitted.add("0x" + f[6:-4].lower())

    rows = []
    for addr, f in pool.items():
        a = addr.lower().replace("0x", "")
        sh = shapes.get(a)
        if not sh or sh["shape"] == "tailcall":
            continue
        if addr.lower() in submitted:
            continue
        if f.get("flagged"):
            continue
        t = twins.get("0x%08x" % int(addr, 16)) or []
        rows.append((sh["shape"], int(f.get("size") or 0), addr, f.get("give_ups", 0),
                     f.get("near_misses", 0), t[0]["conf"] if t else "-",
                     t[0]["fnv"] if t else "-", json.dumps(sh)[:90]))
    rows.sort(key=lambda r: (r[0], r[3], r[1]))
    print("%-10s %-5s %-12s %-4s %-4s %-7s %-11s %s" % ("shape", "size", "address", "gu", "nm", "conf", "twin", "detail"))
    for r in rows:
        print("%-10s %-5d %-12s %-4s %-4s %-7s %-11s %s" % r)
    print("\nusable trivial shapes in the pool:", len(rows))
    return rows


if __name__ == "__main__":
    if "--cross" in sys.argv:
        cross()
    else:
        fetch()
        cross()
