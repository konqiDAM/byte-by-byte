# Session close 7 — 2026-11-13 night: the twin strategy works, and it works on big functions

Read after `SESSION_CLOSE_6_2026-11-13.md`. This file is the delta: what landed, the strategy that produced it, and the
laws learned while doing it.

## State

```
verified 475 (+5 practice)   awaiting 0   strikes 0   INDEX 487 MATCHED · 86 CLOSED · 110 closed-list entries
lessons §19.78 - §20.24   submissions today 60+
flags: 1 pending host build (0x009bb7d0, compile_flags), 16 awaiting review, 5 fixed, 1 reproduced
```

## The strategy that works: TWIN-BEARING FUNCTIONS, INCLUDING BIG ONES

**Five matches tonight**, and four of them came from a function with a high-confidence twin in `rivals/`:

| address | size | how |
|---|---|---|
| `0x0093e980` | 328 B | fresh author, four levers (private calling convention, aggregate-by-value, duplicate expression, volatile pin) |
| `0x00716d90` | 533 B | **twin**; one instruction left -> an inlined `bool`-returning helper (§20.20) |
| `0x00a050e0` | **1183 B** | **twin**; a redundant copy was wrecking the colouring (§20.22) |
| `0x009bb7d0` | **1057 B** | **twin**; the frame order was a *block shape*, not declaration order (§20.24) |
| `0x0092e990` | 272 B | matched under corrected flags, `compile_flags` filed |

**The answer to "are big functions hard": no, not with a twin.** Two big twin-bearing functions matched outright in one
lease each (1183 B and 1057 B, all regions exact). A third reached extent-exact with 4/5 regions and 2 instructions
(`0x00a24db0`, 1165 B). A fourth is **2 bytes** from a match (`0x009bcad0`, 1063 B, 29/29 slots in place). By contrast the
two big functions attempted **without** a twin stalled at 1038/1086 and frame+layout+one-region.

**The pool is large and still mostly unmined:** 160 addresses in `rivals/` carry `twin_conf: high`; 107 are ≥1000 bytes;
`out/_big_twin_pool.json` holds the currently-open ones.

## The five levers that finished the big ones

1. **A redundant copy re-colours the whole function** (§20.22). `v = f(); n = v;` = one value in two registers = one extra
   `mov` = `cache` moves from `ebx` to `ebp`, a stray zero web appears, +12 instructions. Removing it took the instruction
   match **35% -> 88% in one edit**. **If a region's match is 30-60% but the structure looks right, look for two names for
   one value before anything else.**
2. **A block's shape places slots** (§20.24). A nested `{ … }` is a slot-allocation unit; twelve declaration-order levers
   were byte-identical where wrapping `info`+`collector` in a block with the loop gave ORIG's frame order outright.
3. **A vptr store is a position marker** (§20.24). Declaring the object after two other stores moves its vptr store two
   instructions earlier *and* corrupts f3check's derived vtable binding - 15 byte differences from one misplaced store.
4. **An inlined `bool` helper explains `and al,1`** (§20.20). `and al,1` is the bool-return normalisation in the return
   register; no expression produces it. Watch for the traps: an early `return false` leaves an unused 4-byte frame slot, and
   `return a && b` folds back to the bit test.
5. **A refcount decrement needs `(*(short*)&refCount)--`** (§20.22) - plain `--x` on `unsigned short` emits `add word
   [x],0xffff` (imm16) where ORIG has `add word [x],-1` (imm8).

Plus two structural facts that save whole leases: **case values may be the pack's own defect** (`0x00a050e0`'s switch
constants were the FNV build's: list=10 translate=12 convex=13 transform=28), and **`accept_also` decides whether a match
submits normally** (`0x009bcad0`'s `/O2` set is in it - no flag needed).

## The flag oracle, now with a method that needs no sources (§20.23)

**Compile the WHOLE `unit_*.cpp` as-is under each candidate set and byte-compare every body it defines**, masking relocation
bytes. A population result: `0x0091e6a0`'s unit gave **3 of 4 byte-exact under `/O2 /GS`, 0 of 4 under the declared set**;
`0x009f9800`'s gave 7 of 7. It needs no claim and no neighbour source, and it is exactly what the build host does with a
checkpoint. The pack's `/Od /Oy- /GS` label is wrong for a whole region and **the right set differs per file**.

## What is parked, and why

| address | state |
|---|---|
| `0x00a24db0` | 1165 B, extent exact, 4/5 regions, 2 instructions - a measured compiler boundary (§20.19): LEA base/index pick + a store's scheduling slot, 16 variants inert |
| `0x009bcad0` | 1063 B, **2 bytes**, 29/29 slots - a free-list tie (ORIG reuses `radiusA`'s slot, ours `radiusB`'s). Submits normally via `accept_also` |
| `0x0091e6a0` | 1318 B, 57 instructions, R2 exact - x87 **merge depth** 1 vs 2 (§20.23.1); untried: the §20.17 address-of half |
| `0x005ae7e0` | **439/439, identical instruction stream**, one colouring decision - **blocked by a pack defect** (the unit defines the target: `NO_SYMBOL`, §20.21), released with best_code |
| `0x009925d0` | **paused by the platform**: confirmed `file_problem`, pack lacks the required helper header (§20.18) |
| `0x007078d0`, `0x004e0b30`, `0x0090d750`, `0x00763190`, `0x00918e70`, `0x00aa31d0`, `0x00762ab0`, `0x00bf6260` | proved walls, in `out/_closed.txt` with mechanisms |

## Next

1. **Keep taking twin-bearing big functions.** `out/_big_twin_pool.json`; the four launched at close are `0x00a88610`
   (1096), `0x009062d0` (1130), `0x005619e0` (1484), `0x00a6ddd0` (1666).
2. **Run the whole-unit flag oracle first** (§20.23), then author - it decides which set to write against.
3. **Check `accept_also` before planning a `compile_flags` report** - if the set is already accepted, a match is a normal
   submit.
4. Re-check tonight's five `matched` addresses next session (§20.01): a 200 with a submission id is not a verdict, and
   submissions have vanished before.
