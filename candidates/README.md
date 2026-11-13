# Candidates

458 C++ functions written for a matching decompilation of **Fallout 3 (2008)**: each compiles,
with the original toolchain and flags, to machine code byte-identical to the shipped
`Fallout3.exe`. They are reconstructions of the game's code, kept here as the worked examples
behind the chapters — not as a playable source release.

Nothing here comes with the game: no executable, no assets, no data files, no context packs.
These are function bodies only.

## Why they are useful to read

- **They are the ground truth of the story.** `02-harvesting-abandoned-attempts.md` talks about
  residues and extents; these files are what a finished one looks like.
- **The shapes are instructive.** Most are ordinary C++ that happens to compile to the exact
  bytes a 2005-era compiler emitted — including the awkward parts (`this`-adjusting thunks,
  `__stdcall` calling conventions, MSVC-specific intrinsics) that a textbook example would hide.
- **They show the size of the job.** 458 functions is a small fraction of the binary; the point
  of the repository is the method, not the coverage.

## Filenames

`<address>.cpp` — the address of the function in the retail executable. For example
`0x00a269d0.cpp` is the 140-byte function at `0x00a269d0`.

## Provenance, honestly

Every file was produced by the project's own work: written by hand, ported from a known twin in
the public New Vegas decompilation, or iterated from a draft this project generated.

Twenty further matches were **not** included: they were derived from abandoned attempts that
other contributors uploaded to the decompilation service, and those sources are not ours to
republish. They are listed, with the similarity that excluded them, in `.held-back.txt`.

## Licence

These reconstructions are published for study and interoperability. The underlying game code is
(c) Bethesda Softworks. No assets, binaries or data are included, and no warranty is given.
