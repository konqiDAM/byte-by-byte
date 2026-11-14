"""audit_banked_open.py - find banked matches (claims/match_*.cpp) the site still lists as open.

    python exp91/audit_banked_open.py            # report only
    python exp91/audit_banked_open.py --submit   # claim + submit the ones that pass a local re-check

audit_unsubmitted.py skips INDEX status MATCHED, which is exactly the class this finds: a candidate that reached
MATCH locally (so it was banked as match_<addr>.cpp) but was never submitted - 0x0097aa70 was one. The only
truth about submission is the site, so ask function_info per address.
"""
import concurrent.futures as cf
import glob
import hashlib
import io
import json
import os
import re
import subprocess
import sys
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
        except Exception as e:
            if getattr(e, "code", None) == 500:
                continue
            return {"ERR": getattr(e, "code", None), "body": str(e)[:200]}
    return {"ERR": "5xx"}


def info(addr):
    d = post("function_info", {"address": addr})
    return addr, d.get("state"), d


def main():
    submit = "--submit" in sys.argv
    files = glob.glob(os.path.join(ROOT, "claims", "match_*.cpp"))
    addrs = sorted({"0x" + os.path.basename(f)[6:-4].lower() for f in files})
    print("banked candidates: %d files, %d addresses" % (len(files), len(addrs)))
    open_addrs = []
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        for addr, state, d in ex.map(info, addrs):
            if state == "open":
                open_addrs.append((addr, d))
    print("site still lists open: %d" % len(open_addrs))
    for addr, d in open_addrs:
        print("  %-12s size %-5s give_ups %-3s near_misses %-3s flags %s"
              % (addr, d.get("size"), d.get("give_ups"), d.get("near_misses"),
                 ",".join(d.get("flags") or [])))
    if not open_addrs:
        return
    io.open(os.path.join(ROOT, "out", "_banked_open.json"), "w", encoding="utf-8", newline="\n").write(
        json.dumps([{"address": a, "info": {k: d.get(k) for k in
                                            ("size", "flags", "give_ups", "near_misses", "symbol")}}
                    for a, d in open_addrs], indent=1))
    if not submit:
        print("\nreport written: out/_banked_open.json  (re-run with --submit to claim+submit)")
        return
    for addr, d in open_addrs:
        src = os.path.join(ROOT, "claims", "match_%s.cpp" % addr[2:])
        body = io.open(src, encoding="utf-8", errors="replace").read()
        sha = hashlib.sha256(body.encode()).hexdigest()[:16].upper()
        packdir = None
        for pj in glob.glob(os.path.join(ROOT, "claims", "*", "pack.json")):
            try:
                pd = json.load(open(pj))
            except Exception:
                continue
            if "0x" + str(pd.get("address", "")).lower().replace("0x", "") == addr:
                packdir = os.path.dirname(pj)
                break
        if not packdir:
            print("%-12s no pack on disk - skipped" % addr)
            continue
        p = subprocess.run([PY, os.path.join(ROOT, "f3check", "f3check.py"), src, "--pack", packdir],
                           capture_output=True, text=True, errors="replace", env=ENV)
        out = ANSI.sub("", (p.stdout or "") + (p.stderr or ""))
        if "MATCH" not in out:
            print("%-12s local check no longer matches - skipped" % addr)
            continue
        c = post("claim", {"address": addr, "model": MODEL, "harness": "opencode",
                           "effort": "high", "context_mode": "lean"})
        cid = c.get("claim_id")
        if not cid:
            print("%-12s claim failed: %s" % (addr, str(c)[:120]))
            continue
        s = post("submit", {"claim_id": cid, "source": body, "model": MODEL})
        print("%-12s sha=%s claim=%s -> %s" % (addr, sha, cid,
                                               str(s.get("submission_id") or s.get("body") or s)[:200]))
        with io.open(os.path.join(ROOT, "out", "_banked_open_submits.jsonl"), "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"address": addr, "claim_id": cid, "sha": sha,
                                 "server": str(s)[:400]}) + "\n")


if __name__ == "__main__":
    main()
