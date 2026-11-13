"""Fast scorer for any pack (f3check's own comparison logic, in process).

    python exp91/score_pack.py <packdir> <file.cpp> [...]
    python exp91/score_pack.py <packdir> --dir <dir>
"""
import json
import os
import sys
import time

sys.path.insert(0, r"C:\f3decomp\f3check")
os.environ.setdefault("F3CHECK_IMAGE", r"D:\Fallout3\Fallout3.exe")
os.environ.setdefault("F3CHECK_INDEX", r"C:\f3decomp\function_index.json")
os.environ.setdefault("F3CHECK_SYMBOLS", r"C:\f3decomp\f3decomp_symbols.json")
os.environ.setdefault("F3CHECK_TOOLS", r"C:\f3decomp\win_tools")
os.environ.setdefault("F3_MSVC_ROOT", r"C:\f3decomp\vs2005")
os.environ.pop("F3_API_KEY", None)

PACKDIR = os.path.abspath(sys.argv[1])
os.environ["F3CHECK_TREE"] = PACKDIR

import fc_check as K  # noqa: E402


def main():
    m = json.load(open(os.path.join(PACKDIR, "pack.json")))
    entry = K.Entry(addr=int(m["address"], 16), size=m["size"], source=m["source"],
                    symbol=m["symbol"], flags=list(m["flags"]), canary=m.get("canary", False))
    args = sys.argv[2:]
    if args and args[0] == "--dir":
        files = sorted(os.path.join(args[1], f) for f in os.listdir(args[1]) if f.endswith(".cpp"))
    else:
        files = args
    for path in files:
        src = open(path, encoding="utf-8", errors="surrogateescape").read()
        t = time.time()
        res = K.check_candidate(entry, "```cpp\n" + src + "\n```")
        # mirror f3check.py:99-103: the site also accepts every pack.json accept_also set (54 packs on disk,
        # 53 of them listing /Od but accepting /O2).  Without this the fast scorer under-reports a MATCH.
        under = ""
        if res.get("status") not in ("match", "rejected"):
            for alt in (m.get("accept_also") or []):
                r2 = K.check_candidate(K.Entry(addr=entry["addr"], size=entry["size"], source=entry["source"],
                                               symbol=entry["symbol"], flags=list(alt),
                                               canary=entry.get("canary", False)),
                                       "```cpp\n" + src + "\n```")
                if r2.get("status") == "match":
                    res, under = r2, "  UNDER " + " ".join(alt)
                    break
        print("%-42s status=%-8s ndiff=%-5s extent=%-5s errs=%d  %.1fs%s" % (
            os.path.basename(path), res.get("status"), res.get("ndiff_insn"),
            res.get("extent"), len(res.get("errors") or []), time.time() - t, under), flush=True)
        for e in (res.get("errors") or [])[:3]:
            print("      ! " + str(e)[:150])


if __name__ == "__main__":
    main()
