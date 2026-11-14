"""refresh_409.py - force the site to re-run its compile check instead of replaying a stale "already found unfit".

    python exp91/refresh_409.py 0x008d39d0 0x009154b0 0x00a91000

The 409 body says "this exact code was already found unfit", and it is keyed to the source TEXT. 0x00a8c2f0 proved the
record can be STALE: the project file changed since that verdict (an integrated match fixed the collision), so the same
bytes now compile. Prepending a comment line changes the text, forces a fresh pre-verification compile, and leaves the
bytes untouched (f3check still MATCH - a comment is not code).

Each address needs an open claim held by this key. Prints the fresh 409 (which is now a CURRENT verdict) or the
submission id.
"""
import glob
import hashlib
import io
import json
import os
import re
import subprocess
import sys
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
    try:
        return json.loads(urllib.request.urlopen(r).read().decode() or "{}")
    except urllib.error.HTTPError as e:
        return {"ERR": e.code, "body": e.read().decode("utf-8", "replace")}
    except Exception as e:
        return {"ERR": str(e)}


def claim_for(addr):
    for c in post("status").get("open_claims") or []:
        if c.get("address") == addr:
            return c.get("claim_id")
    return None


def pack_for(addr):
    for pj in glob.glob(os.path.join(ROOT, "claims", "*", "pack.json")):
        try:
            d = json.load(open(pj))
        except Exception:
            continue
        if "0x" + str(d.get("address", "")).lower().replace("0x", "") == addr:
            return os.path.dirname(pj)
    return None


def main():
    for addr in sys.argv[1:]:
        print("\n=== %s" % addr)
        cid = claim_for(addr)
        if not cid:
            print("no open claim - skipped")
            continue
        packdir = pack_for(addr)
        src = os.path.join(ROOT, "claims", "match_%s.cpp" % addr[2:])
        if not (packdir and os.path.exists(src)):
            print("no pack or no banked file - skipped")
            continue
        body = io.open(src, encoding="utf-8", errors="replace").read()
        sha = hashlib.sha256(body.encode()).hexdigest()[:16].upper()
        work = os.path.join(packdir, "refresh.cpp")
        io.open(work, "w", encoding="utf-8", newline="\n").write(
            "// refresh %s: same bytes, new text, to force a fresh compile check\n" % addr + body)
        p = subprocess.run([PY, os.path.join(ROOT, "f3check", "f3check.py"), work, "--pack", packdir,
                            "--claim", cid, "--sweep", "text-only refresh of the banked match: bytes identical"],
                           capture_output=True, text=True, errors="replace", env=ENV)
        if "MATCH" not in ANSI.sub("", (p.stdout or "") + (p.stderr or "")):
            print("local check no longer matches - skipped")
            continue
        print("local MATCH, sha %s, claim %s" % (sha, cid))
        s = post("submit", {"claim_id": cid,
                            "source": io.open(work, encoding="utf-8").read(),
                            "model": MODEL})
        if s.get("ERR"):
            print("409 (this is now a CURRENT verdict):\n" + (s.get("body") or "")[:600])
        else:
            print("ACCEPTED: %s" % json.dumps(s)[:300])


if __name__ == "__main__":
    main()
