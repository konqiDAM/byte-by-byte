"""One candidate -> the FULL resolved diff (no truncation), offline.

    python exp91/full_diff.py <packdir> <candidate.cpp> <out.txt>
"""
import io
import json
import os
import sys

PACK = os.path.abspath(sys.argv[1])
CAND = sys.argv[2]
OUT = sys.argv[3]

sys.path.insert(0, r"C:\f3decomp\f3check")
os.environ.setdefault("F3CHECK_IMAGE", r"D:\Fallout3\Fallout3.exe")
os.environ.setdefault("F3CHECK_INDEX", r"C:\f3decomp\function_index.json")
os.environ.setdefault("F3CHECK_SYMBOLS", r"C:\f3decomp\f3decomp_symbols.json")
os.environ.setdefault("F3CHECK_TOOLS", r"C:\f3decomp\win_tools")
os.environ.setdefault("F3_MSVC_ROOT", r"C:\f3decomp\vs2005")
os.environ.pop("F3_API_KEY", None)
os.environ["F3CHECK_TREE"] = PACK

import fc_check as K  # noqa: E402

_orig_aligned = K.aligned_diff


def _wide(*a, **k):
    k['max_lines'] = 500
    return _orig_aligned(*a, **k)


K.aligned_diff = _wide

m = json.load(open(os.path.join(PACK, "pack.json")))
entry = K.Entry(addr=int(m["address"], 16), size=m["size"], source=m["source"],
                symbol=m["symbol"], flags=list(m["flags"]), canary=m.get("canary", False))
src = io.open(CAND, encoding="utf-8", errors="surrogateescape").read()
res = K.check_candidate(entry, "```cpp\n" + src + "\n```")
txt = ["status: %s   ndiff: %s   extent: %s   errors: %d" % (
    res.get("status"), res.get("ndiff_insn"), res.get("extent"), len(res.get("errors") or [])),
    "source: %s" % CAND, "pack:   %s" % PACK, ""]
for e in (res.get("errors") or [])[:6]:
    txt.append("! " + str(e)[:300])
txt += ["", "--- ORIGINAL vs YOURS ---", str(res.get("diff_full") or res.get("diff") or "(identical)")]
if res.get("slots"):
    txt += ["", "--- SLOTS ---", str(res["slots"])]
io.open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(txt) + "\n")
print("%-10s %-8s ndiff=%-5s extent=%-5s" % (m["address"], res.get("status"),
                                              res.get("ndiff_insn"), res.get("extent")))
