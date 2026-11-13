"""Compile a candidate for 0x007641c0 exactly as f3check does, with /FAs, and print the
COMDAT local map ($T temporaries with their offsets) plus the asm of the target function."""
import json, os, re, subprocess, sys, tempfile
from pathlib import Path

PACK = Path(sys.argv[1]).resolve()
CAND = sys.argv[2]
OUT = sys.argv[3] if len(sys.argv) > 3 else r"C:\f3decomp\exp91\last.asm"

sys.path.insert(0, r"C:\f3decomp\f3check")
os.environ.setdefault("F3CHECK_IMAGE", r"D:\Fallout3\Fallout3.exe")
os.environ.setdefault("F3CHECK_INDEX", r"C:\f3decomp\function_index.json")
os.environ.setdefault("F3CHECK_SYMBOLS", r"C:\f3decomp\f3decomp_symbols.json")
os.environ.setdefault("F3CHECK_TOOLS", r"C:\f3decomp\win_tools")
os.environ.setdefault("F3_MSVC_ROOT", r"C:\f3decomp\vs2005")
os.environ.pop("F3_API_KEY", None)
os.environ["F3CHECK_TREE"] = str(PACK)

import fc_check as K

m = json.load(open(PACK / "pack.json"))
entry = K.Entry(addr=int(m["address"], 16), size=m["size"], source=m["source"],
                symbol=m["symbol"], flags=list(m["flags"]), canary=m.get("canary", False))
cand = K.clean_candidate("```cpp\n" + open(CAND, encoding="utf-8").read() + "\n```")
tu = entry.skeleton.rstrip("\n") + '\n#pragma optimize("", on)\n\n// ---- candidate ----\n' + cand

d = Path(tempfile.mkdtemp(dir=r"C:\Users\void\AppData\Local\Temp\opencode"))
tu_p = d / "tu.cpp"; tu_p.write_text(tu, errors="surrogateescape")
asm = d / "tu.asm"
cmd = [sys.executable, "-B", r"C:\f3decomp\win_tools\msvc9.py", "/c", "/nologo"] + list(entry["flags"]) + \
      ["/FAs", "/I" + str(PACK), str(tu_p), "/Fo" + str(d / "tu.obj"), "/Fa" + str(asm)]
r = subprocess.run(cmd, capture_output=True, text=True)
if r.returncode:
    print(r.stdout[-1500:]); sys.exit(1)
text = asm.read_text(errors="surrogateescape")
# the COMDAT block of our function
tag = "FUN_%08x" % entry["addr"]
idx = text.find("COMDAT ?")
blocks = [b for b in re.split(r"(?m)^; Function compile flags", text) if re.search(r"^\?FUN_007641c0@[A-Za-z0-9_@$?]* PROC", b, re.M)]
if not blocks:
    print("target block not found"); sys.exit(1)
b = blocks[0]
open(OUT, "w", encoding="utf-8").write(b)
print(b[:b.find("PROC") + 5])

