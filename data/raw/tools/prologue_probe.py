"""prologue_probe.py - is a pack's /Od label real?  Reads the game image, no claim needed.

    python exp91/prologue_probe.py 0x00961300 0x009f9580 ...

/OD PACKS ARE NOT TRUSTWORTHY.  On 0x00961300 the pack says `/MT /Od /Oy-` but the original is `/O2 /Oy`:
it has `and esp,-16` with `[esp+N]` locals (an optimised frame), scheduled x87 (`fld st(0)`,
`fmul st(0),st(0)`, `fmulp st(2)`, `fxch st(1)`) and FP ops interleaved with `lea`/`push` argument setup -
none of which /Od can emit.  The same draft scores 716 under /Od, 599 under /O2 /Oy-, 520 under /O2 /Oy.

Every /Od candidate must therefore be screened from the BYTES before an agent is spent on it.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(r"C:\f3decomp", "tools"))
import q  # noqa: E402

SIZES = {}
try:
    for p in (r"C:\f3decomp\function_index.json",):
        pass
except Exception:
    pass

RANK = ("fxch", "fmulp", "faddp", "fsubp", "fmul st(", "fadd st(", "fsub st(")


def screen(addr, size):
    code = q.pe_bytes(addr, size)
    lines = []
    for ins in q.disasm(code):
        lines.append("%-8x %-24s %s" % (ins[0], ins[1], ins[2]))
    body = "\n".join(lines)
    flat = body.replace(" ", "")
    aligned = "andesp,0xfffffff0" in flat
    rank = [k for k in ("fxch", "fmulp", "faddp", "fsubp", "fmulst(", "faddst(", "fsubst(") if k in flat]
    if aligned and rank:
        v = "OPTIMIZED (flag wrong)"
    elif aligned or rank:
        v = "LIKELY OPTIMIZED"
    else:
        v = "plausibly /Od"
    return v, aligned, rank, lines[:7]


def main():
    addrs = sys.argv[1:]
    if not addrs:
        pool = json.load(open(r"C:\f3decomp\out\_od_pool.json"))
        addrs = [(x["address"], x["size"]) for x in pool]
        addrs = ["%s:%d" % (a, s) for a, s in addrs]
    counts = {}
    for a in addrs:
        if ":" in a:
            ad, sz = a.split(":")
            addr, size = int(ad, 16), int(sz)
        else:
            addr, size = int(a, 16), 64
        v, aligned, rank, head = screen(addr, size)
        counts[v] = counts.get(v, 0) + 1
        print("%-12s %-24s align=%-5s x87rank=%s" % (hex(addr), v, aligned, ",".join(rank) or "-"))
        if len(addrs) <= 6:
            for l in head:
                print("     ", l.strip())
    print()
    for k, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        print("%-26s %d" % (k, n))


if __name__ == "__main__":
    main()
