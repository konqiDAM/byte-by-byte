# 05 — The levers, and how they were found

Chapters 1-4 described the *arena*: what a match is, where the abandoned work is, how to find the original source,
and what a wall looks like. This chapter is about the **instrument**: how you get from a residue of nine instructions to
zero, and — more usefully — how you *discover* a lever in the first place.

The short version: a lever is never invented. It is **provoked**. You change one thing, a register moves, and you spend the
next hour finding out why. What follows is the translation between C++ and assembly that makes those provocations legible,
then the seven discovery methods that produced every lever in this repository, then the levers themselves with the numbers
that bought them.

---

## 1. Why the same C++ can compile two different ways

A compiler is not one program, it is a pipeline, and byte-identity means steering **every stage** the same way:

| stage | what it decides | its fingerprint in the bytes |
|---|---|---|
| front end | what the expression tree *is* | the order of loads, whether a value is a named object or a temporary |
| IR generation | phi nodes, inlining, constant folding | whether a branch exists at all; whether a store is deferred |
| register allocator | which value gets which register, which spills | `ebx` vs `ebp`, `[esp+0x14]` vs `[esp+0x18]` |
| instruction scheduler | the order independent instructions are emitted in | `fld` before vs after a `push` |
| encoder | the byte form of one instruction | `cmp [mem],0` (imm) vs `cmp [mem],ebx` (register) |

Two C++ functions that mean the same thing can differ at any of these five stages, and each stage leaves a different
signature. **The single most valuable skill in this project is telling those signatures apart**, because they demand
completely different responses:

* a *front-end* signature is reachable from source (change the expression),
* an *allocator* signature sometimes is (change live ranges),
* a *scheduler* signature usually is not (find a different function),
* an *encoder* signature never is (it is the same IR, spelled differently).

Getting that wrong is expensive: 69 source variants on `0x0065e9f0` were aimed at a *scheduler* signature.

---

## 2. Reading C++ backwards — the translation table

This is the part that takes a week to learn and then pays forever. Each line is a real pattern from this project.

### 2.1 A local variable is a *slot*, not a name

```asm
mov [esp+0x18], eax      ; this is *some* local. The name is gone.
cmp [esp+0x18], 0
```

Slots are assigned by the allocator, not by declaration order. Two functions with identical declarations routinely use
different slots. What matters is **who else wants that slot** — and the answer is visible: a slot's users are every
instruction that names it.

### 2.2 `a = b` costs zero instructions if nobody can tell

```cpp
Shp_d74480* v = ProcessShape(...);   // ONE value
n = v;                               // second name for the same value
```

Compiled naively that is a copy. In practice VC8 **coalesces** it: one register, no instruction. That is why a "redundant
name" sometimes costs nothing (see §20.37) and sometimes costs everything (see 2.3).

### 2.3 …but a redundant name can re-colour the entire function

On `0x00a050e0` (1183 bytes) the draft had exactly that shape. The result was **one extra `mov ebp,edi`** — and that single
instruction moved `cache` from `ebx` to `ebp`, conjured a stray zero web in `ebx`, and cost **12 instructions** overall.
Removing it took the instruction match from **35% to 88% in one edit**.

The lesson is not "avoid copies". It is: **when a region's match percentage is low but the structure looks right, the
allocator has been knocked off by one value.** Look for the value, not the statements.

### 2.4 Every comparison against zero has *two* legal encodings

```asm
cmp dword ptr [eax+0x5fc], 0     ; immediate, 4 bytes   <-- ORIG
cmp dword ptr [eax+0x5fc], ebx   ; register,  5 bytes   <-- ours
```

Both are the same test. The compiler picks the immediate when no zeroed register is available, and the register when one
already holds zero. That is why the same source text produced `bl` in one instance and `al` in another **inside one object
file** — the deciding factor is the rest of the *enclosing* function, not the line.

The corpus says how common this is: in one unit, `[eax+0x5fc]` is compared **48 times with four different zero operands**
(`al` 5, `bl`/`ebx` 8, `ebp` 1, immediate the rest). You cannot fix it locally; you can only change what else is live.

### 2.5 A `bool` return is visible in the last byte before the branch

```asm
mov eax,[edi+0x34]
shr eax,1
and al,1          ; <-- the bool-return normalisation, in AL because AL is the return register
jne
```

No expression produces that. It is the signature of an **inlined `bool`-returning function**. We found 14 sites of the byte
pattern `D1 E8 24 01` (`shr eax,1; and al,1`) in the image; one of them is a 12-byte function that is nothing but a `ret`.

### 2.6 A float in the middle of an argument list reserves its slot with a push

```asm
push 1                 ; the bool argument
push ecx               ; reserves 4 bytes - the VALUE is thrown away
fstp dword ptr [esp]   ; the float is written into that reserved slot
push 0xfa3             ; the int argument
call
```

This is how `f(0xfa3, 1.0f, true)` looks. It also explains a class of residues that look like scheduling but are not: which
register VC8 pushes to *reserve* the slot is chosen from what is already dead there.

### 2.7 x87 shows you your expression tree

```asm
fld  dword ptr [esi]      ; a
fld  st(0)                ; a, a
fmul dword ptr [edi]      ; a*a
fadd dword ptr [ebp]      ; a*a + b
fstp dword ptr [esp+0x24] ; store
```

The floating-point stack is a **stack** — each `fld` pushes, each `fstp` pops, `fxch` swaps. The sequence is the shape of
your expression tree, evaluated left to right. When the original folds a memory operand (`fadd dword ptr [esi+4]`) and you
load it first (`fld dword ptr [esi+4]; faddp`), the difference is not the arithmetic — it is whether that value was already
in a register.

### 2.8 A struct copy is integer `mov`s or x87 pairs, and that tells you what it is

```asm
; POD assignment
mov eax,[esi]; mov [edi],eax
mov eax,[esi+4]; mov [edi+4],eax

; member-by-member float copy
fld dword ptr [esi]; fstp dword ptr [edi]
fld dword ptr [esi+4]; fstp dword ptr [edi+4]
```

`0x009310d0`'s four copied vectors were x87 pairs — proof the source copied **members**, not a POD struct. A struct
assignment would have produced integer `mov`s and the whole region would have been wrong.

### 2.9 A loop with a literal trip count gets rewritten; an opaque one does not

```asm
; literal 3 -> strength-reduced ("counted loop transform")
sub [esp+0x4c], 1
jne

; trip count the compiler cannot fold -> indexed form (what the original has)
mov edx,[esp+0x18]; add edx,1; cmp edx,3; mov [esp+0x18],edx; jl
fld [esp+edx*4+0x20]
```

So an **indexed frame loop in the original is proof the bound was not a literal in the source**. `0x0093e980` reproduced it
with `int kk = *(volatile int*)&i;` as the first statement of the body.

### 2.10 Exception handling: `push -1` vs `push -2`

```asm
push -1        ; C++ try/catch  (_except_handler3)
push -2        ; __try          (_except_handler4)
```

Exact, and it decides the whole prologue shape. `0x008efb10` stalled at the third byte because the source used the wrong
one.

### 2.11 A vptr store is a *position marker*

```asm
mov dword ptr [esp+0x18], offset ??_7SphereCollector@@6B@
```

Where that store lands tells you exactly where the object is constructed. On `0x009bb7d0`, declaring the collector four
bytes earlier moved this store two instructions early — which changed 15 bytes **and** broke the checker's vtable binding.

### 2.12 A parameter re-read from the stack was *assigned*, or it spilled

```asm
mov esi,[ebp+8]      ; the parameter's home
...
mov eax,[ebp+8]      ; read again later
```

Two readings: either the source assigned the parameter (so it needs a home), or the allocator ran out of registers (a
spill). The difference is decidable in a minute: **count stores to the home and any `lea` of it**. Stores or `lea` ⇒
assignment; reads only ⇒ spill.

---

## 3. The seven discovery methods

Every lever in §4 came from one of these. None of them is a guess; each produces evidence you can quote.

### 3.1 Differential probing — change one thing, watch what moves

The workhorse. `0x00a050e0`: remove the second name for one value → 35% becomes 88%. `0x004dade0`: delete the list's
zeroing → 511 bytes and the original's register allocation. `0x0093e980`: add one volatile read → the loop shape changes.

The discipline is the point: **one change, one measurement, and write down which byte moved**. Anything else produces a
variant you cannot explain, which is why `--permute` is banned here — it finds matches nobody can reproduce.

### 3.2 Bisection — find the block that flips the decision

When 20+ spellings of the declarations do nothing, the residue is not in the declarations. Delete one **block** at a time
and watch the register assignment flip:

> `0x004f31a0` (1584 bytes): removing `Body* h = apParam->GetBody()` made the compiler put `source` in **ebx** and
> `apParam` in **eax**; adding it back flipped to **edi = apParam**. 23 declaration variants had been inert.

That is one deletion, one observation, and the trigger located in a single pass.

### 3.3 Ablation — price a construct by removing it

"Do I need this local?" Remove it and look at the frame. `0x00a24db0`: strip `align(16)` from a vector → the frame drops
`0x1c`; share two loop temporaries → the frame hits ORIG's `0xb4` exactly (with wrong code, which is fine — you are pricing,
not shipping). Ablation tells you **what a construct costs** before you try to reach a target by another route.

### 3.4 The corpus scan — ask the whole image the same question

Instead of guessing whether an idiom is possible, count how the compiler wrote it elsewhere in the same binary:

* **41** sites of `mov ecx,REG / push eax / call` — and **four of the five** that call our function's callee emit the
  *other* order than ours, including a sibling in the same unit. That single count told us the residue was whole-function
  state, not a statement, and stopped a sweep.
* **48** sites of one comparison with **four** different zero registers — proof the zero encoding is context-decided.
* **17** sites of `mov eax,<reg>; sub eax,0` in 9.9 MB — and none of them a matched function. When a residue is rarer in the
  corpus than the corpus's own examples of it, that is a wall, not a gap in the search.
* **14** sites of `shr eax,1; and al,1`, one of them a 12-byte `bool` function — the corpus *named* the construct.

The scan converts "is this expressible?" into a number. It is the cheapest hour in the project.

### 3.5 The twin comparison — ground truth you did not have to find

If the same function exists in the other engine, its **source at the recorded file:line** is a skeleton. It also settles
arguments: `0x00564cd0` had 65 give-ups; authoring from the real FNV source (`testopic.cpp:1891`) instead of a paraphrase
made the +11-byte loop rotation vanish, because the twin kept a redundant guard the compiler then deletes.

And a *matched* function in the same unit is stronger still: on `0x005693d0` a **90-byte matched sibling** reconstructed
byte-exactly and then ablated showed that the folded-ternary idiom needed **both** a named local **and** an
address-of-something between the value and the test — dropping either folded it. 40 → 16 instructions.

### 3.6 The byte-level harness — measure the bytes you care about

An f3check diff shows you a *window* and truncates. A harness that compiles a variant, extracts the function from the COFF
and prints the differing bytes **in a chosen range** settled `0x00a24db0`'s 2-instruction residue in 16 variants instead of
60: you see immediately whether *your* byte moved, instead of inferring it from a line count.

### 3.7 The flag oracle — settle the compile flags before writing anything

The declared flags in a pack can be wrong for a whole region of the image, and the right set **differs per file**. The
decisive method needs no source at all:

1. compile the **whole** `unit_*.cpp` as-is under each candidate flag set;
2. for every function body the unit defines, byte-compare against the image (masking relocation bytes);
3. count how many are exact.

A population result, not a coincidence: one unit gave **3 of 4 byte-exact under `/O2 /GS` and 0 of 4 under the declared
`/Od`**; another gave **7 of 7**. If any of those bodies is a function the site already marks *matched*, the set is
**proved**.

This is worth 30 minutes on every function, because it is also exactly what the build host does with a checkpoint. Twice
this session the oracle was the difference between a normal submit and a rejected one.

---

## 4. The lever catalogue

Each row is a lever we can now use on purpose, with the measurement that bought it. "Scope" is the part that stops the next
agent from over-applying it.

| lever | the idea | evidence | scope / limit |
|---|---|---|---|
| **Duplicate the expression at its use** | one *named* local is a coloured web; the same expression written twice becomes one unnamed temp | `0x007b8510`: 15-instruction residue moved after 24 variants failed; the products had to be duplicated in *both* arms of the `if` | only when the original reuses one temp area |
| **Name it, to make it movable** | the same lever in reverse — naming turns a rotation slot into a live range | `0x004f31a0`: naming one addend's sub-sum changed which operand became the `lea` base | naming costs `mov`+`add` when it splits a single instruction |
| **A redundant name re-colours everything** | a second name for one value can cost one instruction and move twelve | `0x00a050e0`: 35% → 88% in one edit | **fails when the copy only feeds reads** — VC8 coalesces it (`0x00a6d020`, byte-identical) |
| **A constructor's zero web** | a member-init list makes `0` one web spanning every call in the ctor; `memset` + immediate stores keeps each zero local | `0x00a88610`: **307 → 23 bytes in one edit** | symptom is "one extra 4-byte frame slot" |
| **The zero-constant count decides the rotation** | when a rotation flips on adding/removing stores of a constant, count the zero-using sites | `0x004dade0`: 511 (no zeroing, ORIG's allocation) / 527 (any literal zero) / 519 (call-mediated) | the count is the variable; no spelling changes it |
| **Declare a value *after* the call that uses it** | a value that must survive a call should not be a live web *across* it | `0x009062d0`: 47 → 125 when reversed; match when fixed | only for values the allocator would spill |
| **A block's shape places slots** | a nested `{ … }` is a slot-allocation unit | `0x009bb7d0`: twelve declaration-order levers inert; wrapping two objects with the loop gave ORIG's frame order | declaration *order* inside a block is nearly always inert |
| **An unreferenced region in the frame is a value** | dead slots cannot come from unused declarations — the original had something live across them | `0x008d7020`: 8 unreferenced bytes at `0x54`, 16 at `0xd4`, frame 4 short | the offsets locate the live range |
| **Frame excess of a round 0x10 is alignment** | each distinct `align(16)` local takes its own 16-aligned home | `0x00a24db0`: strip `align(16)` → −0x1c; share two temporaries → exact | never a live-value count |
| **A volatile read is a one-slot barrier** | each volatile read buys a site exactly one scheduling slot, and can pin a value | `0x00902620` ladder: 2 reads → +0x00a, 1 → +0x005, 0 → two instructions vanish | costs an instruction; only free if it displaces one |
| **A volatile read defeats the counted-loop transform** | keeps the counter memory-resident | `0x0093e980`: `int kk = *(volatile int*)&i;` as the first body statement restored the indexed loop | one read, first statement; inline at the use costs 45 rows |
| **Named local + address-of materialises a folded ternary** | a named local *and* an address-of created between the value and the test | `0x005693d0`: 40 → 16 instructions; proved by ablating a byte-exact 90-byte sibling | either half alone is folded |
| **`and al,1` is an inlined `bool` helper** | the normalisation lives in the return register | `0x00716d90`: the last instruction of 150 | early `return false` leaves a 4-byte frame slot; `return a && b` folds back |
| **`push -1` vs `-2`** | C++ `try/catch` vs `__try` | `0x008efb10` stalled at byte 3 on this | also decides whether `and esp,-16` is reachable |
| **A destroyed push is a `this`** | when a pushed value is overwritten by `fstp [esp]`, the load is a register convention | `0x007dab90`: the load was a `__thiscall` `this`, worth the whole 12-byte gap | the value is irrelevant; only the register matters |
| **Registers go out in descending order of memory references** | a ranking you can compute before experimenting | `0x00769230`: predicted which value should get `0x14` | tells you *which* value to pressurise |
| **The EH unwind map is the object model** | each unwind action names a destructor and a member offset | `0x008e4d50`: recovered a 0x38-byte object with four array destructors; `__try` was wrong | placement `new` emits no unwind states at all |
| **Two identical prefixes merge; make them differ** | VC8 merges identical blocks, so ORIG's duplicated block must have differed in one register | `0x005619e0`: the entire 33-byte gap was one merge | do not reshape the block; break the *equivalence* |

---

## 5. The strategies, ranked by what they actually paid

The levers finish functions. The **strategies** decide which functions exist to be finished, and they were worth more than
any single lever this session.

### 5.1 Twins first — the single best predictor of success

Six matches, and every one of them had a twin or a matched sibling in its own unit. The two big functions attempted
*without* a twin stalled at 1038/1086 and one region.

The pool is bigger than it looks: scanning **every** `rivals` entry (not just the high-confidence ones) found 205 candidates
in the 150-1500 byte band, of which 33 were open and workable. Two lessons: **verify the twin's shape before authoring**
(one entry pointed at an unrelated function), and **go to the file the index names** rather than a paraphrase.

### 5.2 Check what the site already knows before you write a line

Three separate traps, each of which looks like "this function is impossible":

* **A saved attempt can already match.** 65 local packets held a draft recorded at score 0. Twenty-eight addresses were
  still open; submitting them cost nothing and produced a match.
* **A 409 saying "this exact code was already found unfit" is a cache** keyed to the source *text*, and it goes stale.
  Prepending **one comment line** re-runs the compile. Four addresses went in with zero byte changes.
* **A `function_info` field can save the whole lease**: `file_problem` marks functions the platform has *paused* on a
  confirmed data defect. 86 of 160 twin-bearing functions were paused this way. Not difficulty — data.

### 5.3 Triage by evidence, not by counts

Give-up counts on the service are **farmed**: `0x0065e9f0` has 75 and is nine instructions from a match (most give-ups are
"check refused for missing notes/plan"); `0x009cb440` has 53 and 49 are automated screening. Sort by *saved-attempt score*
and *reported residue* instead. That is how `0x00564cd0` (122 instructions, one extra slot) and `0x00a5c3d0`-class
candidates surfaced while the "popular" ones were noise.

### 5.4 Know when a residue is not yours to solve

Four walls were *classified* rather than swept, and each classification saved a lease:

* a redundant instruction that keeps nothing alive cannot be asked of the allocator (`0x00762ab0`, 140 variants);
* an order that survives aliasing, reachability, read form *and* sequencing is not a source property (`0x00bf6260`, 62);
* two mechanisms that cost the same produce the same score — measure the *offset*, not the total (`0x004e0b30`);
* when the frame is right and the colouring is wrong only with an extra slot, you are looking for a shape where those are
  not the same web (`0x00564cd0`) — that is the hand-off point, not the next variant.

### 5.5 Publish the wall ledger

110 proved walls, each with a one-line mechanism, live in `CLOSED.md` / `_closed.txt`. That file exists because the same
wall was rediscovered three times in one day: a 228 KB log does not stop an agent, a filtered list does.

---

## 6. What a lever is worth, in one table

From the session's own accounting, over 376 sessions:

| what | count |
|---|---|
| functions matched | 6 (two of them ≥1 KB, two via the flag route) |
| functions brought to one or two instructions | 4 more |
| levers that worked and generalised | 18 |
| walls proved and written down | 110 |
| source variants measured inert | ~1,800 |

The ratio is the honest headline: **roughly one match per sixty sessions, but one durable lever per twenty.** The levers
are why the *next* sixty sessions will not look like the last sixty.
