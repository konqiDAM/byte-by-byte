"""claim_many.py - claim a list of addresses and print claim_id/expires as JSON (for the launch briefs).

    python exp91/claim_many.py 0x009310d0 0x00568be0 ...
"""
import json
import io
import os
import sys
import urllib.error
import urllib.request

API = "https://f3decomp.com/api/v1/"
KEY = io.open(os.path.expanduser(r"~\.f3decomp_key"), encoding="utf-8").read().strip()
MODEL = "DeepSeek V4.1 Flash"


def post(path, payload=None):
    r = urllib.request.Request(API + path, data=json.dumps(payload or {}).encode(),
                               headers={"Authorization": "Bearer " + KEY,
                                        "User-Agent": "Mozilla/5.0",
                                        "Content-Type": "application/json"})
    try:
        return json.loads(urllib.request.urlopen(r).read().decode() or "{}")
    except urllib.error.HTTPError as e:
        return {"ERR": e.code, "body": e.read().decode("utf-8", "replace")[:200]}
    except Exception as e:
        return {"ERR": str(e)}


def main():
    out = {}
    for a in sys.argv[1:]:
        c = post("claim", {"address": a, "model": MODEL, "harness": "opencode",
                           "effort": "high", "context_mode": "resume"})
        cid = c.get("claim_id")
        print("%-12s %s %s" % (a, cid or json.dumps(c)[:150], c.get("expires") or ""))
        if cid:
            out[a] = cid
    io.open(os.path.join(r"C:\f3decomp\out", "_claims_now.json"), "w", encoding="utf-8",
            newline="\n").write(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
