"""twins_extract.py - put the FNV twin's SOURCE in the agent's hand.

    python exp91/twins_extract.py 0x00a89680 0x0070a9a0 ...

For each address: resolve the twin (exact symbol mapping first, then the scored matcher), find the
function in the FNV tree at the recorded file:line, extract it by brace matching, and write

    C:\\f3decomp\\out\\<address>\\twin.txt

with the provenance header and the source.  The human owner has authorised using this code directly
on this private project, so the agent may copy and adapt it - but the FNV body can be a different
engine version, so the F3 bytes stay the authority.
"""
import json
import os
import pickle
import re
import sys

ROOT = r"C:\f3decomp"
FNV_ROOT = os.path.join(ROOT, "twins", "fnv_decomp")
FUNHEX = re.compile(r"FUN_([0-9a-fA-F]{8})")


def load():
    syms = {}
    for e in json.load(open(os.path.join(ROOT, "f3decomp_symbols.json"), encoding="utf-8"))["functions"]:
        syms.setdefault(int(e["address"], 16), e["symbol"])
    twins = json.load(open(os.path.join(ROOT, "twins", "cache", "twins.json"), encoding="utf-8"))
    try:
        fnv = {e["addr"]: e for e in pickle.load(open(os.path.join(ROOT, "twins", "cache", "fnv_index.pkl"), "rb"))}
    except Exception:
        fnv = {}
    return syms, twins, fnv


def resolve(addr, syms, twins, fnv):
    m = FUNHEX.search(syms.get(addr, ""))
    if m:
        hit = int(m.group(1), 16)
        e = fnv.get(hit) or {}
        if e:
            return dict(kind="exact", fnv="0x%08x" % hit, src=e.get("src"), line=e.get("line"),
                        name=((e.get("scope") + "::") if e.get("scope") else "") + str(e.get("name")))
    t = twins.get("0x%08x" % addr) or []
    if t and t[0].get("conf") in ("high", "medium"):
        c = t[0]
        return dict(kind=c["conf"], fnv=c.get("fnv"), src=c.get("src"), line=c.get("line"),
                    name=((c.get("scope") + "::") if c.get("scope") else "") + str(c.get("name")))
    return None


def extract(path, line):
    try:
        lines = open(path, encoding="utf-8", errors="replace").read().split("\n")
    except OSError:
        return None, "file not readable"
    start = max(0, (line or 1) - 1)
    # find the opening brace at or after the recorded line
    open_i = None
    for i in range(start, min(len(lines), start + 200)):
        if "{" in lines[i]:
            open_i = i
            break
    if open_i is None:
        return None, "no opening brace within 200 lines"
    depth = 0
    end_i = None
    for i in range(open_i, min(len(lines), open_i + 4000)):
        depth += lines[i].count("{") - lines[i].count("}")
        if depth == 0 and i > open_i - 1:
            end_i = i
            break
    if end_i is None:
        return None, "unbalanced braces within 4000 lines"
    head = max(0, open_i - 3)
    return "\n".join(lines[head:end_i + 1]), None


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    syms, twins, fnv = load()
    for a in argv:
        addr = int(a, 16)
        t = resolve(addr, syms, twins, fnv)
        out_dir = os.path.join(ROOT, "out", "%08x" % addr)
        os.makedirs(out_dir, exist_ok=True)
        dst = os.path.join(out_dir, "twin.txt")
        # never clobber a good extract: a manual extraction (or another resolver) may have found one
        # this resolver cannot (a name or unit twin), and re-running would replace it with NO TWIN
        if os.path.isfile(dst):
            try:
                head = open(dst, encoding="utf-8", errors="replace").read(64)
            except OSError:
                head = ""
            if "NO TWIN RESOLVED" not in head and "EXTRACT FAILED" not in head:
                print("%-12s kept the existing extract (%d B)" % (a, os.path.getsize(dst)))
                continue
        if not t or not t.get("src"):
            open(dst, "w", encoding="utf-8").write("NO TWIN RESOLVED for 0x%08x\n" % addr)
            print("%-12s NO TWIN" % a)
            continue
        path = os.path.join(FNV_ROOT, t["src"].replace("/", os.sep))
        body, err = extract(path, t.get("line"))
        hdr = ("# FNV twin of 0x%08x\n"
               "# confidence: %s   fnv address: %s\n"
               "# source: %s:%s\n"
               "# function: %s\n"
               "#\n"
               "# AUTHORISED: the project owner has stated this is a private project and the FNV code\n"
               "# may be copied/adapted directly.  CAVEAT: the FNV *body* can belong to a different\n"
               "# engine version and FNV's Havok is the SSE build while Fallout 3's is x87 - the SHAPE\n"
               "# is reliable, the detail is not.  The F3 bytes are the authority.\n"
               "#\n# ---- source follows ----\n\n"
               % (addr, t["kind"], t["fnv"], t["src"], t.get("line"), t["name"]))
        with open(dst, "w", encoding="utf-8", newline="\n") as f:
            f.write(hdr)
            f.write(body if body else "EXTRACT FAILED: %s\n" % err)
        print("%-12s %-7s %-11s %s:%s  -> %s (%d lines)"
              % (a, t["kind"], t["fnv"], t["src"], t.get("line"),
                 os.path.relpath(dst, ROOT), (body or "").count("\n") + 1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
