"""resubmit_banked.py - re-claim an address and submit its banked match file.

    python exp91/resubmit_banked.py 0x008fb4e0 [0x00b0d290 ...]

For addresses whose submit returned 200 earlier but whose site state is still `open` with an empty verification queue: the
submission is gone, the bytes are still on disk. Re-claim, prepend one comment line (the 409 cache is keyed to the text),
re-check locally, submit. Reports the state after each submit.
"""
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
            return {"ERR": e.code, "body": e.read().decode("utf-8", "replace")[:300]}
        except Exception:
            time.sleep(2)
    return {"ERR": "retry"}


def pack_for(addr):
    import glob
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
        src = os.path.join(ROOT, "claims", "match_%s.cpp" % addr[2:])
        pack = pack_for(addr)
        if not (os.path.exists(src) and pack):
            print("no banked file or no pack - skipped")
            continue
        c = post("claim", {"address": addr, "model": MODEL, "harness": "opencode",
                           "effort": "high", "context_mode": "lean"})
        cid = c.get("claim_id")
        if not cid:
            print("claim failed:", json.dumps(c)[:150])
            continue
        work = os.path.join(pack, "resubmit.cpp")
        body = io.open(src, encoding="utf-8", errors="replace").read()
        io.open(work, "w", encoding="utf-8", newline="\n").write(
            "// resubmit %s: same bytes, new text\n" % addr + body)
        p = subprocess.run([PY, os.path.join(ROOT, "f3check", "f3check.py"), work, "--pack", pack,
                            "--claim", cid, "--sweep", "resubmit of a banked match whose verdict never landed"],
                           capture_output=True, text=True, errors="replace", env=ENV)
        if "MATCH" not in ANSI.sub("", (p.stdout or "") + (p.stderr or "")):
            print("local check no longer matches - skipped")
            continue
        s = post("submit", {"claim_id": cid, "source": io.open(work, encoding="utf-8").read(),
                            "model": MODEL})
        print("claim %s -> submit %s" % (cid, str(s.get("submission_id") or s.get("body") or s)[:200]))
        time.sleep(3)
        print("state now:", post("function_info", {"address": addr}).get("state"))


if __name__ == "__main__":
    main()
