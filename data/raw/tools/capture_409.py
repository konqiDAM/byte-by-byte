"""capture_409.py - re-submit the 9 banked-but-open candidates with the server's rejection text captured.

    python exp91/capture_409.py

audit_banked_open.py dropped the HTTPError body, which is the only part worth having: it names the TU line and the
type that failed to compile. Re-submits against the claims it already created (no new claims).

NOTE: callers must not use a post() that replaces the body with str(e) - that is the bug this repairs.
"""
import glob
import io
import json
import os
import urllib.error
import urllib.request

API = "https://f3decomp.com/api/v1/"
KEY = io.open(os.path.expanduser(r"~\.f3decomp_key"), encoding="utf-8").read().strip()
ROOT = r"C:\f3decomp"
MODEL = "DeepSeek V4.1 Flash"


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


def main():
    rows = [json.loads(l) for l in io.open(os.path.join(ROOT, "out", "_banked_open_submits.jsonl"),
                                            encoding="utf-8") if l.strip()]
    out = []
    for row in rows:
        addr, cid = row["address"], row["claim_id"]
        src = os.path.join(ROOT, "claims", "match_%s.cpp" % addr[2:])
        body = io.open(src, encoding="utf-8", errors="replace").read()
        s = post("submit", {"claim_id": cid, "source": body, "model": MODEL})
        text = s.get("body") or json.dumps(s)
        print("\n=== %s  claim %s" % (addr, cid))
        print(text[:700])
        out.append({"address": addr, "claim_id": cid, "err": s.get("ERR"), "body": text})
    io.open(os.path.join(ROOT, "out", "_banked_open_409.json"), "w", encoding="utf-8",
            newline="\n").write(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
