"""fetch_pack.py - download a claim's pack into claims/<claim_id>/ and unpack it.

    python exp91/fetch_pack.py clm_xxx

POST /packet gives pack_url + signature; GET /api/v1/pack/<claim_id> with the auth header returns the tar.gz
(auth header required - a plain GET 404s). Then tar xzf it in place.
"""
import io
import json
import os
import subprocess
import sys
import tarfile
import urllib.error
import urllib.request

API = "https://f3decomp.com/api/v1/"
KEY = io.open(os.path.expanduser(r"~\.f3decomp_key"), encoding="utf-8").read().strip()
ROOT = r"C:\f3decomp"


def post(path, payload=None):
    r = urllib.request.Request(API + path, data=json.dumps(payload or {}).encode(),
                               headers={"Authorization": "Bearer " + KEY,
                                        "User-Agent": "Mozilla/5.0",
                                        "Content-Type": "application/json"})
    try:
        return json.loads(urllib.request.urlopen(r).read().decode() or "{}")
    except urllib.error.HTTPError as e:
        return {"ERR": e.code, "body": e.read().decode("utf-8", "replace")[:300]}


def main():
    cid = sys.argv[1]
    d = os.path.join(ROOT, "claims", cid)
    os.makedirs(d, exist_ok=True)
    p = post("packet", {"claim_id": cid, "context_mode": "lean"})
    io.open(os.path.join(d, "packet.json"), "w", encoding="utf-8", newline="\n").write(
        json.dumps(p, indent=1))
    print("packet: size %s flags %s symbol %s" % (p.get("size"), p.get("flags"), p.get("symbol")))
    r = urllib.request.Request(API + "pack/" + cid,
                               headers={"Authorization": "Bearer " + KEY, "User-Agent": "Mozilla/5.0"})
    try:
        blob = urllib.request.urlopen(r).read()
    except urllib.error.HTTPError as e:
        print("pack download failed:", e.code, e.read().decode("utf-8", "replace")[:200])
        return
    tgz = os.path.join(d, "pack.tar.gz")
    open(tgz, "wb").write(blob)
    with tarfile.open(tgz) as tf:
        tf.extractall(d)
    print("unpacked into", d, "->", sorted(os.listdir(d)))


if __name__ == "__main__":
    main()
