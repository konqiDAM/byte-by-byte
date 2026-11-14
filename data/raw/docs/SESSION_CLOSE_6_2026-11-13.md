# Session close 6 — 2026-11-13 (evening wave): the 409 was lying, and ten new laws

Read after `SESSION_CLOSE_5_2026-11-13.md`. This file is the delta: what changed, what was learned, what is running.

## State

```
verified 471 (+5 practice)   strikes 0   submissions today 24
INDEX 2041 addresses: 483 MATCHED · 89 CLOSED (was 39) · 28 open near-misses
lessons 19.88 sections end at 19.87
```

## The finding that matters: `already found unfit` is a cache, and it goes stale

The platform's 409 `this exact code was already found unfit (it matches the pack but not the project file)` is **stored
per source text and never re-evaluated**. Every verified match is integrated into the project file, so a verdict from a
week ago describes a file that no longer exists. **Prepending one comment line** changes the text hash, re-runs the
pre-verification compile, and leaves every byte untouched.

Four addresses went in on that trick alone, with **zero byte changes**: `0x00a8c2f0`, `0x00a91000`, `0x008d39d0`,
`0x009154b0`. Two of them had been written off in writing as a type mismatch and a symbol defect.

Tells that a 409 is stale: the `tu.cpp` line number **moves with the length of the inserted text**; it names members the
candidate does not contain; or it complains about a symbol that is the address's own index symbol. Tool:
`exp91/refresh_409.py <addr> [...]`.

Corollary that cost a claim: an **unfit verdict closes the claim**, so finishing needs a re-claim by address.

## The banked-but-open class (§19.78)

`audit_unsubmitted.py` skipped INDEX status `MATCHED` — exactly the class "matched, banked, never submitted".
`exp91/audit_banked_open.py` asks `function_info` per banked file: **9 of 482** were still open. All nine are now
submitted, and **six needed no byte change at all**:

| address | fix | outcome |
|---|---|---|
| 0x008fb4e0 | hoisted one prototype | submitted |
| 0x00b0d290 | `::g_memoryManager` (§19.80) | submitted |
| 0x00a4d720 | hoisted one prototype (§19.81) | submitted |
| 0x00a8c2f0 0x00a91000 0x008d39d0 0x009154b0 | stale 409, comment only (§19.82) | submitted |
| 0x00668c30 | real work - see §19.86 | **verified matched** |
| 0x00615e50 | re-declare the stub's declaration (§19.87) | submitted |

## Ten laws from this wave (details in `handoffs/lessons-rival-code.md`)

* **19.78** a MATCH is necessary, not sufficient — the pack is a *skeleton* of the unit, the site compiles the full
  project file, so a name the candidate invents can collide only in the project build.
* **19.79** a **deliberately redundant** instruction cannot be asked of the allocator. `0x00762ab0` needed one dead
  `mov eax,ebx`; 140 variants, corpus has 17 such sites in 9.9 MB and none is a matched function. Closed.
* **19.80** a 409 naming a **missing member** is usually a **name-lookup scope** bug inside a reopened `fnv_<addr>`
  namespace — qualify with `::`, do not rewrite the type. (Renaming can also drop you to `no_symbol`.)
* **19.81** `C3861` **followed by** `C2365` on the same name = a declaration that exists but sits *below* its first use.
  Hoist the prototype verbatim; it emits no code.
* **19.82** the stale 409 cache, above.
* **19.83** a run of register ties is usually **one cycle rotated by a slot**; the lever is *before the last offset where
  the two listings agree*. Dead upstream temps prove nops cannot rotate a cycle.
* **19.84** the file-fit check counts **MSVC anonymous-label renumbering** as a change: `0x0097aa70` compiled three ways
  leaves `0x00979830` instruction-identical and still fails. Flagged `checker_problem` / `scope: unit` → **8 functions
  flagged in one call**.
* **19.85** when the emitted order survives changes to aliasing, reachability, read form **and** sequencing, the order is
  not a source property. `0x00bf6260`, 62 variants, both axes exhausted. Closed.
* **19.86** a MATCH can bind a **library lookalike** (`_std_target`): the risk class is "includes a std header or defines a
  template **and** never names `FUN_<addr>`". Exactly 1 of 482 banked files was in it - and it was the false one. The real
  target was `std::string::replace(const char*, size_type)`.
* **19.87** your candidate **replaces** the project's stub, so the stub's declarations leave the TU — including ones other
  matched functions use. **A 409 naming a function your candidate never calls means exactly this**: re-declare it
  verbatim (types get a forward declaration; a definition gives C2129/C2084).

## Running at close

7 retry agents on previously abandoned work, all claimed, all expiring ~14:22Z:

| address | size | why it was abandoned | lever |
|---|---|---|---|
| 0x009310d0 | 654 | "listed /Od but the target is /O2 code; 4 instructions from exact" | flag oracle |
| 0x00568be0 | 708 | "draft needs real /O2 work; listed /Od flags look wrong" | flag oracle |
| 0x00918e70 | 895 | 210/258; `ebx` goes to `filterInfo`, nothing crosses the call | non-rematerialisable web + §19.76 |
| 0x00763190 | 523 | ndiff 2: `mov ecx,edi` before/after the argument push | §19.76 / §19.83 |
| 0x00aa31d0 | 449 | ndiff 2: dead-load temp `eax` vs `ecx` | §19.83 rotation |
| 0x004e0b30 | 360 | ndiff 2: dtor-arg `lea eax` vs `lea ecx`, ~730 variants | live-set change only |
| 0x0090d750 | 163 | ndiff 2: store one instruction early, ~246 variants | §19.76 first, then barrier probe |

Plus `0x00931eb0` (1891 B, released by the other agent): packet says `/Od /Oy-`, an open report claims `/O2`. Its agent
runs the **flag oracle** — build the unit's already-matched neighbours (`0x00925b30` 407 B, `0x0092eaa0` 286 B) at both
flag sets; whichever reproduces their sizes is the unit's true flags. Note the false lead: `__declspec(align(16))` forces
`and esp,-16` **even at /Od**, so an aligned frame is not evidence of /O2.

## The reusable instruments

1. `exp91/refresh_409.py` — stale 409 → fresh compile (comment only).
2. `exp91/audit_banked_open.py` — banked vs site state; run after every wave.
3. `exp91/flag_unit_fit2.py` — file a `checker_problem` on a unit (needs an open claim, `note` ≤ ~256 chars).
4. `exp91/fetch_pack.py` — the pack folder can be missing from disk even when an older claim folder exists.
5. `exp91/claim_many.py`, `exp91/add_sessions.py` — wave plumbing.
6. The **flag oracle** (build a matched neighbour at both flag sets) — the only objective way to settle `/Od` vs `/O2`.

## Not started

`0x009a9cb0` (1839 B, same flags complaint, 5 give-ups, no draft), `0x00902620` (278 B, 54 give-ups), `0x00711660`
(30 B, 156 give-ups), `0x00575a30` (920 B), `0x00a42140` (219 B), `0x0098df40` (1362/1364, rotation wall). All `open`.

## Outcomes of the retry wave (all seven resolved, 14:05Z)

| address | outcome |
|---|---|
| **0x00568be0** | **MATCH 708/708, 0 diffs** under the file's real flags `/MT /O2 /GS /EHsc /Gy`; `compile_flags` proof filed (host recompiles <=30 min, credits an exact match, and runs the same set on saved code for every other open function of that file) - §19.93 |
| 0x00918e70 | 210 -> **215/258** via the volatile self-assign, then the allocator law proved - §19.91 - closed |
| 0x00aa31d0 | `ecx` mechanism found (an inlined member body's folded `this` takes `eax` first), order proved mutually exclusive in VC8 - §19.92 - closed |
| 0x004e0b30 | two independent "+2" mechanisms looked like one; prefix immaterial, the decision is future-use - §19.88 - closed |
| 0x0090d750 | the only dial that moves the pair overshoots by 41 slots - §19.89 - closed |
| 0x00763190 | a **sibling in the same unit with the same statement emits the other order**, so the statement is right and the order is whole-function state - §19.96 - closed |
| 0x009310d0 | 639/654 under the real flags; wall = parameter home (ORIG reloads `[ebp+0xc]`, we promote) - §19.95 - held |

**One win, five proved walls, one wall named with a lever.** The win came from the flag oracle, not from matching code: six
of the seven retries had been abandoned for reasons that had nothing to do with the source.

**Correction to §19.90, learned on 0x00568be0 (19.90.1):** the flag set is **per file**. `0x00931eb0`'s file is
`/MT /O2 /GS- /EHsc /Gy`; `0x00568be0`'s is `/MT /O2 /GS /EHsc /Gy` (its original carries the stack cookie). Never carry a
set across files - run the oracle in the file you are in, against that file's own matched neighbour.

**Still open at the end of the wave:** `0x009f9800` (1413 B, flags proven `/O2 /GS-` for its file, agent working R1..R6;
a match there is the only route to a flag proof for that file) and `0x00931eb0` (651/1891, R10-R22 unwritten).
