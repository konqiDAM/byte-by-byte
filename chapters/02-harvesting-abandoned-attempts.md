# 02 — Harvesting the attempts nobody finished

The pool was not empty when we started. Every function in it had already been claimed and
given up on by someone else, and the service kept their work: for each abandoned attempt it
served us the source they had written, plus their own note saying what they thought was still
wrong.

That is the single most useful resource in matching decompilation after the binary itself. A
failed attempt is not wasted work, it is a **measurement**: somebody has already proved that a
particular source shape compiles to these bytes and not those.

## The loop we used

```
claim one address  ->  read its history  ->  download the source of every checkpoints
                   ->  give the claim back  ->  compile and score all of it offline
```

Two properties of that loop made it cheap:

- **Giving up never counts against you.** The service treats a released claim as neutral, so
  reading a function's history costs nothing but requests.
- **The scoring is offline.** Once the sources are on disk we compile them ourselves, so the
  expensive part (the compiler) does not touch the site at all.

We ran 2 856 of these sessions in two days: 1 482 distinct functions, 515 distinct drafts that
we had never seen before, and 2 679 context packs.

## What a "pack" gives you

Alongside the source, the service hands you the context a function needs to compile in
isolation: headers, the declarations the original translation unit had, and the compiler flags
recorded for that function. A pack is the difference between "here is 2 000 bytes of C++" and
"here is C++ that compiles".

It also gives away something structural, which we only noticed later: a pack carries a
`unit_*.cpp`, and a **unit is the compiler's view of one original source file**. Two functions
in the same unit were in the same file in the original game. That observation became the
biggest lever in the whole project — see [03-twins.md](03-twins.md).

## Measuring yield instead of guessing

The first instinct is to work the functions with the most prior attempts: if eight people tried,
there must be a lot of material. Measured, that instinct is backwards.

| prior near misses | drafts that landed within 2 instructions |
|---|---|
| 0–2 | 14 % |
| 21–50 | 4 % |

Popular functions are popular because they are hard. The same inversion showed up in size:

| size band | usable rate |
|---|---|
| ≤ 255 B | 25 % |
| 256–511 B | 29 % |
| 512 B–1 KB | 19 % |
| 1–4 KB | 15 % |
| > 4 KB | 3 % |

So the ordering we ended up with was: **small functions first, paying address ranges first, and
popularity last** — the opposite of the intuitive order, and worth roughly 4× on yield per
request.

## The dead ranges

Two address ranges in this binary cannot be matched, no matter how good the source is:

- the **speedtree** try/catch bodies, whose recorded span ends at the exception-handling
  funclets the compiler emits after the function, so the compiled extent can never equal the
  recorded size;
- the **CRT** functions, which are detached `__finally` fragments reading a frame they do not
  own — not standalone functions at all.

That was ~250 of the remaining small functions, i.e. a third of the pool. Detecting it and
skipping it up front was the cheapest single decision of the project.

## What the harvest is actually for

Two outcomes, and only one of them is obvious:

1. **A draft close enough to finish.** 59 of 1 204 scored drafts were within 2 instructions of
   a match, and 249 compiled clean at the original's exact size.
2. **A map of the walls.** The contributors' notes, aggregated, say where the project keeps
   getting stuck — and some of those places turned out to be compiler decisions no source can
   express. That is what [04-the-walls.md](04-the-walls.md) is about.
