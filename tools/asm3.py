"""Side-by-side listing: ORIGINAL vs YOURS, every instruction with its offset (offline).

    python exp91/asm3.py <packdir> <candidate.cpp> [out.txt]
"""
import difflib
import json
import os
import re
import sys

PACK = os.path.abspath(sys.argv[1])
CAND = sys.argv[2]
OUT = sys.argv[3] if len(sys.argv) > 3 else None

sys.path.insert(0, r"C:\f3decomp\f3check")
os.environ.setdefault("F3CHECK_IMAGE", r"D:\Fallout3\Fallout3.exe")
os.environ.setdefault("F3CHECK_INDEX", r"C:\f3decomp\function_index.json")
os.environ.setdefault("F3CHECK_SYMBOLS", r"C:\f3decomp\f3decomp_symbols.json")
os.environ.setdefault("F3CHECK_TOOLS", r"C:\f3decomp\win_tools")
os.environ.setdefault("F3_MSVC_ROOT", r"C:\f3decomp\vs2005")
os.environ.pop("F3_API_KEY", None)
os.environ["F3CHECK_TREE"] = PACK

import fc_check as K  # noqa: E402

CAP = {}


def grab(entry, coff, sym, binds, extent, namer, max_lines=70, derived=None, extra=None):
    addr = entry["addr"]
    n = entry["size"]
    ob = entry.original
    shown = set()
    if derived:
        binds = dict(binds)
        for name, t in derived.items():
            if name.startswith("!"):
                continue
            m = re.match(r"\?*(?:FUN|DAT|str|flt|dbl|off|PTR|unk)_([0-9a-fA-F]{8})(?![0-9A-Za-z_])", name)
            if m and K.in_image(int(m.group(1), 16)):
                binds[name] = int(m.group(1), 16)
            elif not (t in K.FUNC_STARTS or t in namer.prefer or (K.in_image(t) and not K.is_code_addr(t))):
                binds.pop(name, None)
                shown.add(name)
    lb, fake = K.linked_bytes(coff, sym, entry, binds, extent)
    nm = K.Namer(dict(namer.prefer))
    for name, t in fake.items():
        nm.prefer[t] = K.short_name(name) + ("" if name in shown else "(?unbound)")
    orl = K.render_function(ob, addr, n, nm)
    cl = K.render_function(lb, addr, extent, nm)
    CAP["orig"] = orl
    CAP["ours"] = cl
    return "", 0, [], []


K.aligned_diff = grab


def main():
    m = json.load(open(os.path.join(PACK, "pack.json")))
    entry = K.Entry(addr=int(m["address"], 16), size=m["size"], source=m["source"],
                    symbol=m["symbol"], flags=list(m["flags"]), canary=m.get("canary", False))
    src = open(CAND, encoding="utf-8", errors="surrogateescape").read()
    res = K.check_candidate(entry, "```cpp\n" + src + "\n```")
    strip = lambda s: re.sub(r"\s*;.*$", "", s)
    o = [(off, strip(t)) for off, t in CAP["orig"]]
    c = [(off, strip(t)) for off, t in CAP["ours"]]
    lines = ["status %s ndiff %s extent %s" % (res.get("status"), res.get("ndiff_insn"), res.get("extent")), ""]
    sm = difflib.SequenceMatcher(None, [t for _, t in o], [t for _, t in c], autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                lines.append("%5s  %-42s | %5s  %s" % ("%04x" % o[i1 + k][0], o[i1 + k][1],
                                                     "%04x" % c[j1 + k][0], c[j1 + k][1]))
        else:
            for k in range(i1, i2):
                lines.append("ORIG %04x  %-40s |" % (o[k][0], o[k][1]))
            for k in range(j1, j2):
                lines.append("YOURS%04x  %-40s |" % (c[k][0], c[k][1]))
            lines.append("      %-40s |" % ("-" * 40))
    out = "\n".join(lines) + "\n"
    if OUT:
        open(OUT, "w", encoding="utf-8", newline="\n").write(out)
        print("written %s (ndiff=%s extent=%s)" % (OUT, res.get("ndiff_insn"), res.get("extent")))
    else:
        print(out)


if __name__ == "__main__":
    main()
