# The tools

Reference implementations of the ideas in this repository, not turnkey software. They assume a
local project root (`C:\f3decomp` by default) holding the game image, a pinned VS2005 SP1
compiler, the check tooling, and an API key for the decompilation service. Nothing here contains
a key, and the game is not included.

| tool | what it does |
|---|---|
| `rivals_import.py` | the harvester: parallel "lanes" (one per size band + pool kind), claim a batch, read history, download sources, score offline. Enforces a hard ceiling on simultaneous claims, retries `giveup`, and writes every failure to one error file. |
| `rivals_twins.py` | the twin layer: exact symbol match → similarity matcher → note names (4 filters) → unit anchoring by vote, with a precedence rule (a lower source never overwrites a higher one). |
| `rivals_delta.py` | ranks already-harvested functions worth re-reading, i.e. where someone may have uploaded better code since. |
| `score_pending.py` | scores every downloaded-but-unscored draft in parallel (one compiler process per candidate). |
| `harvest_map.py` | what is left in the pool: per band, swept vs missing, and how many carry a usable near miss. |
| `harvest_targets.py` | where to spend next: yield per size band and per address prefix, plus the dead ranges. |
| `score_pack.py` | in-process scorer: compiles a candidate against a pack and prints `status / ndiff / extent / errs`. |
| `asm3.py` | original vs candidate, instruction by instruction **with offsets** — the diff a normal checker truncates. |
| `full_diff.py` | the whole diff to a file, no elision. |
| `fasmap.py` | the compiler's own frame map, for stack-slot differences. |
| `prologue_probe.py` | detects a pack whose declared optimisation flags are wrong, by reading the function prologue. |
| `pool_now.py` | snapshots the open pool to JSON, so the analysis scripts do not hit the API. |

## What these encode

Three habits are worth copying even if you never run them:

1. **Bound your concurrency by the resource that actually limits you.** Harvesting is limited by
   the API's request budget (~9 requests per function, 25 000 per hour), not by CPU; scoring is
   limited by cores. They are different pools and they want different thread counts.
2. **Score offline, always.** Every compile against a downloaded pack is free. The only thing
   the network is for is fetching sources.
3. **Write the failure down in one place.** A single error file with the address and the claim
   id turned a transient server failure from "21 functions stuck for an hour" into a retry that
   takes 30 seconds.

## Known rough edges

Honest list, because these matter if you reuse them:

- paths default to `C:\f3decomp`; the environment variables the checker already uses
  (`F3CHECK_INDEX`, `F3CHECK_SYMBOLS`, `F3CHECK_TOOLS`, `F3_MSVC_ROOT`) override most of them,
  but a few are literal.
- `rivals_twins.py` reads the similarity matcher's cache and the New Vegas source tree; both are
  separate projects and are not vendored here.
- the scoring output format is tuned to one particular checker implementation.
