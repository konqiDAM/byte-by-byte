# 03 — Finding the original source instead of guessing

The most expensive part of matching decompilation is not the compiler, it is the guessing: what
was this function for, which struct fields does it touch, what order do the branches come in.
Every hour saved on that is an hour that goes into the bytes.

Fallout 3 has an unusual advantage: **Fallout: New Vegas** runs the same engine, was built from
the same codebase two years later, and its decompilation is public. A function that survives
unchanged between the two games has a **twin** — the same original source, already
reconstructed, with a file and a line number.

166 of the ~1 480 functions we harvested ended up with a named twin. Getting there was four
different techniques, each with a different precision.

## 1. The symbol (exact)

Some packs carry the original symbol, not just `FUN_0041a300`. If that symbol matches an entry
in the New Vegas index, the twin is known with certainty — 25 functions.

## 2. A similarity matcher

The general tool ranks New Vegas functions for a given Fallout 3 function using signals that
survive recompilation:

- **string literals** and their order,
- **non-trivial constants** (a magic number is a fingerprint),
- **float constants** and `dynamic_cast` RTTI type names,
- **callee names**, resolved through a second pass,
- **link order** — both games keep file order and, mostly, function order inside a file, so a
  function between two known twins has its twin between their counterparts.

Each signal is weighted by rarity, so a common string counts for little and a weird one counts
for a lot. Restricting to high/medium confidence gave 331 functions.

## 3. The unit (the cheap structural win)

This one needs no matcher at all, just a bit of accounting:

- 2 740 downloaded packs contained only **184 distinct units**;
- one unit covered **234 functions** — they are all in the same original source file;
- if two functions of a unit independently point at the same New Vegas file, the unit's file is
  identified;
- then **every** function in that unit has its twin among that file's functions, typically ~50,
  instead of among 11 000.

That turns an unbounded search into reading one file. 43 units were resolved this way, covering
315 functions. One caveat we had to add later: a unit inside the dead address ranges is
identified but still unworkable, so it is marked and sorted last rather than handed to an agent.

## 4. Names asserted in notes (small, but precise)

Contributors sometimes write what a function *is* ("ActorD::UpdateDismemberedLimbs"),
and a qualified name is enough to look it up. Done naively this is 90 % noise: a stand-in class
name like `NiRenderedTexture::GetType` appeared in fifteen unrelated drafts.

Kept only when **all four** hold:

1. it comes from a contributor's **note**, i.e. an assertion, not from anywhere in the draft;
2. it is **qualified** (`Class::Method`, or the Havok `hkpXxx_Method` form);
3. it is **rare in the New Vegas index** — at most two entries share the name;
4. it appears in **at most two** harvested functions, so a stand-in name is filtered out.

That cut 23 candidates to 4 twins, with no false positive we could find. Small, but it costs
nothing and it grows as the harvest grows.

## Why it matters

For a matched function, the twin is worth more than any draft: a draft is somebody's guess that
compiles to within a few instructions, a twin is the actual source with the actual field names.
Reading 40 lines beats three hours of trial and error — and on the 59 drafts that were already
within two instructions, the twin usually says exactly which instruction to fix.
