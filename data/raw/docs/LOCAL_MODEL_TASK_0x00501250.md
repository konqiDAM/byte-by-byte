# LOCAL MODEL TASK — 0x00501250 (`FUN_00587440`, 214 bytes)

Byte-identical C++ reconstruction of one Fallout 3 function. Everything you need is inline below; the static facts
(disassembly, the twin source, the declarations) are exact and must not be second-guessed. The open questions are the
**flags** and the **truncation idiom**, and both are stated at the end.

---

## Environment

Windows, PowerShell. These must be set in every shell:

```powershell
cd C:\f3decomp
$env:F3CHECK_IMAGE="D:\Fallout3\Fallout3.exe"
$env:F3CHECK_INDEX="C:\f3decomp\function_index.json"
$env:F3CHECK_SYMBOLS="C:\f3decomp\f3decomp_symbols.json"
$env:F3CHECK_TOOLS="C:\f3decomp\win_tools"
$env:F3_MSVC_ROOT="C:\f3decomp\vs2005"
$env:F3_API_KEY=(Get-Content "$env:USERPROFILE\.f3decomp_key" -Raw).Trim()
```

Python: `C:\Users\void\AppData\Local\Programs\Python\Python310\python.exe`
Compiler: VS2005 SP1 only (`cl 14.00.50727.762`). No other version produces matching bytes.

```powershell
# the check you will run constantly
& "C:\Users\void\AppData\Local\Programs\Python\Python310\python.exe" f3check\f3check.py `
  claims\clm_3b03a197d17d46ddb907\cand.cpp --pack claims\clm_3b03a197d17d46ddb907 `
  --claim clm_3b03a197d17d46ddb907 --sweep "variant description"
```

It prints `MATCH` (you are done), or the first differing instructions with `ORIG`/`YOURS` labels and the compiled extent.

---

## The target

```
address   0x00501250
size      214 bytes          (the compiled extent MUST be 214)
symbol    ?FUN_00587440@@YAHPBUNiPoint3@@@Z
          -> int __cdecl FUN_00587440(const NiPoint3* aCoord)
pack      claims\clm_3b03a197d17d46ddb907   (unit_e35e6114d671.cpp + two headers)
declared flags   /MT /Od /Oy- /GS /EHsc /Gy /GF      <-- see "The flag question" below
```

The pack already declares everything you need (do **not** redeclare these):

```cpp
struct NiPoint3 { /* many methods */ float x; float y; float z; };
int __cdecl TruncateFloatToInt(float);
int __cdecl _FNV_Finite(double);
int __cdecl _FNV_IsNaN(double);
int __cdecl FUN_00587440(const NiPoint3* aCoord);   // the target itself
```

Put **only the function body** in `cand.cpp`. f3check prepends the unit's declarations itself; a second declaration of
anything above is a compile error.

---

## The original, byte for byte (214 bytes, offsets from 0x00501250)

```
0000  55                     push ebp
0001  8bec                   mov ebp, esp
0003  83e4c0                 and esp, 0xffffffc0          <-- 64-byte aligned frame
0006  83ec3c                 sub esp, 0x3c
0009  56                     push esi
000a  8b7508                 mov esi, [ebp+8]             ; aCoord
000d  d906                   fld  dword [esi]             ; aCoord->x
000f  83ec08                 sub  esp, 8
0012  dd1c24                 fstp qword [esp]             ; float -> double for the call
0015  e82b067000             call 0xc01895                ; _FNV_Finite
001a  83c408                 add  esp, 8
001d  85c0                   test eax, eax
001f  0f84a7000000           je   0x0050131c              ; !finite(x) -> return 0x7fff7fff
0025  d94604                 fld  dword [esi+4]           ; y
0028  83ec08                 sub  esp, 8
002b  dd1c24                 fstp qword [esp]
002e  e812067000             call 0xc01895
0033  83c408                 add  esp, 8
0036  85c0                   test eax, eax
0038  0f848e000000           je   0x0050131c
003e  d94608                 fld  dword [esi+8]           ; z
0041  83ec08                 sub  esp, 8
0044  dd1c24                 fstp qword [esp]
0047  e8f9057000             call 0xc01895
004c  83c408                 add  esp, 8
004f  85c0                   test eax, eax
0051  7479                   je   0x0050131c
0053  d906                   fld  dword [esi]             ; x again
0055  83ec08                 sub  esp, 8
0058  dd1c24                 fstp qword [esp]
005b  e8fa057000             call 0xc018aa                ; _FNV_IsNaN
0060  83c408                 add  esp, 8
0063  85c0                   test eax, eax
0065  7565                   jne  0x0050131c              ; isnan(x) -> return 0x7fff7fff
0067  d94604                 fld  dword [esi+4]
006a  83ec08                 sub  esp, 8
006d  dd1c24                 fstp qword [esp]
0070  e8e5057000             call 0xc018aa
0075  83c408                 add  esp, 8
0078  85c0                   test eax, eax
007a  7550                   jne  0x0050131c
007c  d94608                 fld  dword [esi+8]
007f  83ec08                 sub  esp, 8
0082  dd1c24                 fstp qword [esp]
0085  e8d0057000             call 0xc018aa
008a  83c408                 add  esp, 8
008d  85c0                   test eax, eax
008f  753b                   jne  0x0050131c
0091  d906                   fld  dword [esi]             ; ---- the truncation idiom ----
0093  d95c2438               fstp dword [esp+0x38]        ; float temp slot
0097  d9442438               fld  dword [esp+0x38]        ; reload it
009b  db5c2434               fistp dword [esp+0x34]       ; -> int slot  (TruncateFloatToInt)
009f  d94604                 fld  dword [esi+4]           ; same for y
00a2  d95c243c               fstp dword [esp+0x3c]
00a6  d944243c               fld  dword [esp+0x3c]
00aa  db5c2438               fistp dword [esp+0x38]
00ae  8b442434               mov  eax, [esp+0x34]
00b2  8b4c2438               mov  ecx, [esp+0x38]
00b6  c1f80c                 sar  eax, 0xc                ; >> 12
00b9  0fbfc0                 movsx eax, ax                ; (short)
00bc  c1f90c                 sar  ecx, 0xc
00bf  0fb7d1                 movzx edx, cx                ; (unsigned short)
00c2  c1e010                 shl  eax, 0x10
00c5  0bc2                   or   eax, edx                ; key = (short)x<<16 | (ushort)y
00c7  5e                     pop  esi
00c8  8be5                   mov  esp, ebp
00ca  5d                     pop  ebp
00cb  c3                     ret
00cc  b8ff7fff7f             mov  eax, 0x7fff7fff         ; the failure return
00d1  5e                     pop  esi
00d2  8be5                   mov  esp, ebp
00d4  5d                     pop  ebp
00d5  c3                     ret
```

Read it as source: six sequential tests (three `!finite`, three `isnan`, both short-circuiting to the same
`return 0x7fff7fff;` at the bottom), then two truncations, then a 32-bit key assembly.

---

## The FNV twin — same function in the other engine (authorised to copy/adapt)

```
// @fnv 0x00587440
int __cdecl TESWorldSpace_GetKeyForWorldCoord(const NiPoint3* aCoord)
{
    int icellx;
    int icelly;

    if (!_FNV_Finite(aCoord->x) || !_FNV_Finite(aCoord->y) || !_FNV_Finite(aCoord->z) || _FNV_IsNaN(aCoord->x) ||
        _FNV_IsNaN(aCoord->y) || _FNV_IsNaN(aCoord->z))
    {
        return 0x7fff7fff;
    }

    icellx = TruncateFloatToInt(aCoord->x) >> 12;
    icelly = TruncateFloatToInt(aCoord->y) >> 12;
    return TESWorldSpace::BuildCellKey((short)icellx, (short)icelly);
}
```

The FNV body can belong to a different engine version, so **the F3 bytes are the authority** - use the twin for shape, not
for detail. Note F3 has no `BuildCellKey` call here: the key is assembled inline (`shl 0x10; or`).

---

## Starting point (already measured - do not repeat this work)

This source:

```cpp
int __cdecl FUN_00587440(const NiPoint3* aCoord)
{
    int icellx;
    int icelly;

    if (!_FNV_Finite(aCoord->x) || !_FNV_Finite(aCoord->y) || !_FNV_Finite(aCoord->z))
        return 0x7fff7fff;
    if (_FNV_IsNaN(aCoord->x) || _FNV_IsNaN(aCoord->y) || _FNV_IsNaN(aCoord->z))
        return 0x7fff7fff;

    icellx = TruncateFloatToInt(aCoord->x) >> 12;
    icelly = TruncateFloatToInt(aCoord->y) >> 12;
    return ((short)icellx << 16) | (unsigned short)icelly;
}
```

compiles to:

| flags | extent | vs 214 |
|---|---|---|
| `/MT /O2 /GS /EHsc /Gy` | 192 | -22 |
| `/MT /O2 /Oy- /GS /EHsc /Gy` | 196 | -18 |
| `/MT /O2 /GS- /EHsc /Gy` | 192 | -22 |
| `/MT /O1 /GS /EHsc /Gy` | 174 | -40 |
| `/MT /Os /GS /EHsc /Gy` | **210** | -4 |
| `/MT /Od /GS /EHsc /Gy /GF` (declared) | 229 | +15 |

So the six-call preamble and the key assembly are probably right (the shape matches), and **the missing/extra bytes are in
the frame and the truncation**. The remaining work is the two questions below.

---

## The two open questions

**1. Which flag set is this file really built with?** The declared set is `/MT /Od /Oy- /GS /EHsc /Gy /GF`, but the code
does not look like `/Od`: it uses **esp-relative** temporaries (`[esp+0x34]`, `[esp+0x38]`, `[esp+0x3c]`) and an
`and esp,0xffffffc0` **64-byte aligned** frame, both of which are optimized-build shapes. `/Od` at `/Oy-` gives ebp-relative
locals.

Note in this project the pack's `/Od` label is **wrong for a whole region of the image**, and the correct set also varies
per file - so do not trust it. The reliable way to settle it: **compile another function from the same `unit_*.cpp` whose
source you know** (if one exists) and see which set reproduces it byte for byte. If the unit defines no other function body,
settle it by extent as above and report which set got closest.

**2. What produces the store/reload/fistp truncation?** The original does **not** call `TruncateFloatToInt` - it inlines it
as three instructions with a float temp and an int temp:

```
fstp [esp+0x38]     ; store the float into slot X
fld  [esp+0x38]     ; reload it
fistp [esp+0x34]    ; convert into slot Y
```

That store-to-one-slot / convert-from-another-slot pattern is what you get from a helper with **its own named float
parameter and its own int local**, inlined:

```cpp
static __inline int TruncateFloatToInt_(float f) { int i = (int)f; return i; }   // for example - verify
```

Test several forms: a direct `(int)x` cast; a named float local then the cast; an inlined helper with a float parameter; an
inlined helper with both a float and an int local; a `__forceinline` version. **Each changes which slots the two temps use**,
and ORIG wants the float in `+0x38` and the int in `+0x34` for x, then `+0x3c`/`+0x38` for y - i.e. the slots overlap
between the two truncations.

Also worth testing: `TruncateFloatToInt` as an **out-of-line** call (if it is a real function, you would see a `call`, so
this is probably wrong - but one check settles it).

---

## Rules

* **Real C++ only.** No inline assembly, no `__emit`, no hard-coded absolute addresses, no `#pragma optimize`. Use the
  names the pack gives you.
* **Never submit a non-match.** A match is a match: f3check prints `MATCH` and the extent is 214.
* Iterate in this loop: edit `cand.cpp` → run f3check → read the **first** differing instruction only → change one thing →
  repeat. Do not change three things at once.
* If the extent is wrong, the frame or a call is wrong; fix that **before** looking at individual instruction bytes.
* A useful diagnostic: `--full-diff <file>` writes the whole listing to a file, so you can see the differing pairs in
  context rather than only the first one.

## Report back

* the final source (or the best one, as `cand.cpp` contents),
* the flag set that reproduced the extent,
* the extent and the number of differing instructions at that point,
* and, if not a match, the single first differing instruction pair with its offset.

## Context that is deliberately not here

Do not search this repo for previous attempts at this address. The point is to see what a local model does with a clean
brief: the twin, the bytes, and the two named questions.
