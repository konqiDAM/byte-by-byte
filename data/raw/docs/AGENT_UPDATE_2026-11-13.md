# AGENT UPDATE — 2026-11-13 evening (read this before your next variant)

Everything below is **measured today**, not theory. Two of our own laws were **refuted** by measurement, so read the
corrections before applying them. Full detail: `handoffs/lessons-rival-code.md` §19.78–§20.15; state:
`SESSION_CLOSE_6_2026-11-13.md`.

## CORRECTION 1 — the RTM hypothesis is DEAD (§20.08.1)

`0x005693d0` and `0x00707af0` were both suspected of coming from a VS2005 **RTM** build, because ORIG keeps an idiom that
SP1 folds. Both suspicions are now refuted:

| unit | matched function in the same unit | size |
|---|---|---|
| `0x005693d0`'s | `FUN_00565710` | **matched, 500 B** |
| `0x00707af0` / `0x007078d0`'s | `0x00707450` | **matched, 981 B** |

SP1 demonstrably produces matching bytes for both files. **Do not spend another minute on the build hypothesis** — the
residues are source / enclosing-function state, and they are solvable.

## CORRECTION 2 — §19.95 needs a two-minute test before you apply it (§19.95.1)

§19.95 says "a parameter ORIG reloads from `[ebp+N]` was assigned by the source". On `0x00702430` that was **refuted**:
ORIG read `anim`'s home 4x with **zero stores and zero `lea`** of it — the reloads were a spill, not a memory-homed
parameter.

**Test before applying §19.95:** count `mov reg,[ebp+N]` for the home, and count stores to it and any `lea` of it.
Stores or `lea` ⇒ §19.95 applies. Reads only ⇒ it is a spill, and you are in the colouring family below.

## THE BIG ONE — the zero-register / invariant-hoist family (§20.14, §20.13)

This is now **the project's biggest blocker**, and it has one cause. Four functions died on it today: `0x007078d0`,
`0x00707af0`, `0x004dade0`, `0x008e4d50`.

**The proof, and it is airtight.** `0x00707450` is matched, and its source compiles **twice in one object file**. VC8
emits **both** forms from byte-identical text:

| instance | emitted |
|---|---|
| standalone COMDAT | `cmp byte [esi+248], bl` / `cmp [eax+1532], ebx` |
| the same body **inlined** into the matched function | `cmp byte [esi+248], al` / `cmp [eax+1532], 0` |

Both instances contain `xor ebx,ebx` and `lea ebp,[ebx+2]` — **both know `ebx == 0`, and one still uses the immediate.**
Corpus: that compare appears **48 times in that unit with four different zero operands** (`al` 5, `bl`/`ebx` 8, `ebp` 1,
immediate the rest).

**So: the form is decided by the rest of the enclosing function, not by your statement.**

* **Do not respell the compare.** 25 variants (`0x00707af0`), 10 (`0x007078d0`), 7 (`0x004dade0`), 5 structural levers
  (`0x008e4d50`) — all inert. Transplanting the matched twin's chain verbatim is inert too; it inlines to the same IR.
* **The variable is pressure**: how many disjoint webs want a zero, and what else is live across them.
  `0x008e4d50`: ORIG shares one zero in `ebx` across **four** disjoint webs; ours puts it in `edi`, which spills
  `e4`/`key`/`pair` (frame 0x40 vs 0x3c).
* **The one untested lever, named independently twice:** **add a value that is live across the chain**, raising the
  pressure so the zero cannot be shared. `0x00707af0`'s agent identified the exact missing pieces: the `interaction` /
  `eligible` / `type` / `scale` locals the matched twin keeps live *before* its chain.

**The measurement that would settle it (30 minutes, do this before any more variants):** disassemble 8–10 of the 48
corpus sites in that unit and count live callee-saved registers at each. If `al`-sites cluster at **low** live counts and
`bl`-sites at **high** ones, the rule is confirmed and the fix becomes "add or remove one live value". Report the table
even if you get no match — it unblocks four functions.

## The invariant hoist, separately (§20.13)

* A **volatile re-read** is the *only* source-level way to forbid an invariant load hoist. Assignment is folded;
  address-taking is transparent to VC8 (measured: `Anim** pa = &anim` was byte-identical).
* Killing the hoist does **not** hand the register to ORIG's value: the **loop counter** claims it, because ORIG's
  `xor esi,esi` happens **before** `push ebx`. That is the §19.83 one-slot rotation — the lever is **where the counter's
  zero is materialised**, not the parameter.

## The flag oracle — run it first, always

* The `/Od /Oy- /GS` label is **wrong for a whole region**, and the correct set **differs per file**:
  `0x00931eb0`'s file `/MT /O2 /GS- /EHsc /Gy`; `0x00568be0`'s and `0x005693d0`'s `/MT /O2 /GS /EHsc /Gy`;
  `0x009bb7d0`'s `/MT /O2 /GS /EHsc /Gy` (its packet says `/Od /Oy-`).
* **Best method (needs no neighbour source): compile the WHOLE `unit_*.cpp` as-is under each candidate set and
  byte-compare every function body it defines, masking relocation bytes.** Four or seven bodies agreeing is a
  *population* result, not a coincidence — on `0x0091e6a0`'s unit: **3 of 4 byte-exact under `/O2 /GS`, 0 of 4 under
  the declared set**; on `0x009f9800`'s: 7 of 7 under `/O2 /GS-`. It is also exactly what the build host does with a
  checkpoint.
* **Method when sources are available:** pick a **`matched`** function in the same `unit_*.cpp`, build the unit under each candidate set with
  `win_tools\msvc9.py`, and compare **bytes**, not sizes. That is the only reliable answer.
* **An `align(16)` local does NOT imply `/O2`** — at `/Od` it also emits `and esp,-16`, but with
  `push ebx; mov ebx,esp; …` and `ebp`-relative slots, versus `push ebp; mov ebp,esp; and esp,-16; sub esp,N` with
  `[esp+..]` temporaries.
* A match under a **corrected** set is **not submittable**: checkpoint it and report; the build host credits an exact match
  (proven today on `0x00568be0` and filed for `0x0092e990`).

## Levers that produced matches today

1. **Two scalars read from the stack ⇒ one 8-byte aggregate passed by value** (`0x0093e980`, matched).
2. **A pushed value destroyed by `fstp dword ptr [esp]` is a `__thiscall` `this`**, not an argument (`0x007dab90`).
3. **A volatile read pins a value with zero cost** — used three ways today: scheduling barrier (§19.71), defeating the
   counted-loop transform (§19.99: `int kk = *(volatile int*)&i;` as the **first** statement), and pinning entry-block
   register saves (§20.10).
4. **Duplicate the expression at its use** instead of naming it, when the original has one unnamed temp (§19.76).
5. **Private calling convention** — `static __declspec(noinline)` plus a visible caller, when ORIG has no prologue and the
   argument arrives in a register (§20.05/§20.10).
6. **EH unwind map = object model.** `push -1 / push <handler>` ⇒ dump the `FuncInfo`; each unwind action names a
   destructor and the member offset, which gives the class layout and construction order directly (§20.15).
7. **Twin index first.** `ls rivals/<addr>/` — a twin is a skeleton, not a hint (`0x005693d0` = FNV `0x00622590`).

## Rules that have not changed

Never submit a non-match. Never release a claim you intend to keep working on. Do not file flags (the main session does).
Never `--permute`. `progress\<addr>.md` with the UTC time after 15 minutes. A 409 that names a function your candidate
never calls means your body deleted a project-stub declaration another matched function needed — re-declare it verbatim
(§19.87). And a **200 with a submission id is not a verdict** (§20.01): only `matched` counts.
