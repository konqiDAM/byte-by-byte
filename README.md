# Byte by Byte

A field log from an experiment in **matching decompilation**: rebuilding a released PC game —
Fallout 3 (2008) — as C++ that a compiler turns back into the *identical machine code*, one
function at a time.

This repository is the story, not the source. It contains what we measured, the tools we
built, and the things that surprised us. It does **not** contain the game, any decompiled
function body, or code other people uploaded to the service we worked with.

If you have never decompiled anything, start with
[chapters/01-what-matching-means.md](chapters/01-what-matching-means.md).

## The idea in one paragraph

A decompiler can turn `Fallout3.exe` back into something that *looks* like C++, but it is a
guess: variable names are lost, types are inferred, and the output rarely compiles back to the
same bytes. Matching decompilation refuses to guess. You claim one function, write C++ by
hand, compile it with the **same compiler and flags the original used**, and compare the
machine code byte for byte. When the bytes are identical, you have not approximated the
original source — you have reconstructed it. The project is done when every function matches.

## What the numbers looked like

The account worked a pool of functions that other contributors had already given up on, so
the interesting question was never "can this be decompiled" but "which of these is worth the
next hour".

| stage | count |
|---|---|
| functions where the pool had been given up on | 1 590 |
| functions harvested for their code (one claim each) | 1 482 |
| drafts that compiled at all | 1 204 |
| drafts that compiled **clean at the original's exact size** | **249** |
| of those, carrying a known Fallout: New Vegas twin | 130 |
| at ≤ 2 instructions from a match | 59 |
| probe sessions spent to get there | 2 856 |

Two lessons hid in that funnel.

**Most "code" is not usable code.** Of 1 204 drafts that compiled, only 249 had the original's
exact byte size. A draft whose size differs can never match, no matter how the source is
spelled — the extent comes from the compiler, not from the author's intent. Everything else
is a lead at best.

**Small functions pay, and popularity lies.** Yield by size band, measured on the same pool:

| size band | scored drafts | usable | usable rate | ≤ 2 instructions off |
|---|---|---|---|---|
| ≤ 255 B | 284 | 72 | 25 % | 28 |
| 256–511 B | 200 | 58 | 29 % | 8 |
| 512 B–1 KB | 344 | 66 | 19 % | 14 |
| 1–4 KB | 345 | 52 | 15 % | 9 |
| > 4 KB | 31 | 1 | 3 % | 0 |

The functions with the *most* prior attempts were the *least* productive: the ones with 21–50
near misses landed a close draft 4 % of the time, the ones with 0–2 landed one 14 % of the
time. Popular functions are popular because they are hard.

## Finding the original source instead of guessing

The single biggest lever was not writing better C++. It was realising that many Fallout 3
functions have a **twin**: the same original function in the New Vegas decompilation, which is
public. Same engine, same file order, often the same function order within a file.

So before writing a line, we asked: has someone already published this function's source?

| how the twin was found | functions |
|---|---|
| the pack's own symbol names a New Vegas function | 25 |
| weighted similarity matcher (strings, constants, callee names, link order) | 331 |
| a name asserted in a contributor's note, four strict filters | 4 |
| the pack's *unit* identities the original file, so the twin is one of its ~50 functions | 43 files, 315 functions |

Two of those deserve a note.

**Unit anchoring** was the cheap win. A "unit" is the compiler's view of one original source
file, and 2 740 downloaded packs turned out to contain only **184 distinct units** — one unit
covered 234 functions. Anchor two functions in a unit to the same New Vegas file and the whole
unit's original file is known: the search drops from 11 000 candidate functions to ~50.

**Name anchoring, done naively, is 90 % noise.** A stand-in class name like
`NiRenderedTexture::GetType` appeared in fifteen unrelated drafts. Keeping a name only when it
comes from a contributor's *note*, is *qualified* (`Class::Method`), is rare in the New Vegas
index (≤ 2 entries) and rare across drafts (≤ 2 addresses) cut 23 candidates down to 4 real
twins, with no false positives we could find.

## What the walls looked like

Not everything is source shape. A handful of one-instruction differences turned out to be
compiler decisions no C++ can express, and the honest thing was to stop:

- **`add reg, -imm` becomes `sub reg, imm`** on a branch-merge edge. Measured over ~235
  spellings; only a memory home keeps the `add`, and it never fits.
- A 12-byte temporary's **frame slot**: the original places it at a 16-byte-aligned offset, the
  compiler lays it out contiguously, and no source shape forces the alignment without also
  emitting a stack-alignment prologue the original does not have.
- **sret slots**: three separate one-instruction near misses all ended on the same
  hidden-return-pointer reservation. Documented once, then closed, so nobody spends the hour
  twice.

## What we would tell someone starting

1. **The compiler is not a detail, it is the problem.** Only one version produced matching
   bytes. Every flag matters.
2. **Measure the yield, not the effort.** Track usable-per-request and close-drafts-per-band;
   the pool's shape decides where the next hour goes.
3. **Take the code that already exists.** Harvesting other contributors' abandoned attempts
   beat writing from scratch, and finding the original source beat both.
4. **Write down the walls.** A one-instruction residue that nobody can explain will be
   re-attempted by the next person unless it is recorded with the failed spellings.

## Data

The numbers above are generated from the working set and committed as small tables:

- `data/funnel.csv` — the harvest funnel
- `data/yield-by-size.csv` — yield per size band
- `data/ndiff-distribution.csv` — how far the best draft is, in instructions
- `data/method-coverage.csv` — how functions were twinned

No API keys, claim ids, pack contents, or decompiled bodies are in this repository; `.gitignore`
enforces that, and the history was scanned before the first push.

## Licence

Tooling: MIT. Prose and data: CC BY 4.0.
