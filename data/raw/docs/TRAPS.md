# TRAPS — read this page before any work. One screen. Everything here has cost real time or a real risk.

## Strike risks (never do these)

1. **Never submit a non-match.** A failed verification is a strike.
2. **Never submit a match whose flags differ from the pack's declared flags.** The verifier compiles with the
   pack's set. If your candidate is exact only under the corrected flags, **checkpoint it and report**; the
   maintainers' build host compiles the checkpoint under the proven set and credits it.
3. **Verify every match claim before acting on it.** Check the file's `sha256[:16]` actually changed since the
   last measurement, and re-run the check yourself. An agent has reported `ndiff 0` on an unchanged file.
4. **One live agent per claim.** Subagents never call `claim` or `giveup`; the main session owns both.
5. **Release before the lease ends.** Swarm leases are **1 hour**; a lapsed claim is the one thing that can
   pause claiming. Lease times are **UTC**; the local clock is **UTC+1** — never compare them by eye.
6. **`already found unfit` is a stale cache, not a verdict** (2026-11-13, §19.82). It is keyed to the source
   *text* and never re-evaluated, so it blocks candidates that compile fine today. **Prepend one comment line**
   and resubmit — the bytes are unchanged and the pre-verification compile re-runs. Four addresses went in that
   way with zero code changes (`0x00a8c2f0`, `0x00a91000`, `0x008d39d0`, `0x009154b0`). Tool:
   `python exp91\refresh_409.py <addr> [...]`. Tells: the `tu.cpp` line number moves with your text length, or
   it names a symbol your candidate does not use.
7. **An unfit verdict closes the claim**, so finishing needs a re-claim by address — get the class right the
   first time, especially §19.87: a 409 naming a function your candidate never calls means your body deleted the
   project stub's declaration and another matched function needed it. Re-declare it verbatim (declarations emit
   no code); a *definition* gives C2129/C2084.
8. **A 200 with a `submission_id` is not a verdict** (§20.01). Seven of tonight's submissions returned 200 and
   then vanished: no verdict, no strike, queue empty, `state: open` an hour later. Re-check every address you
   submitted in a **later** session — `matched` means it landed; `open` with `awaiting_verification: 0` means it
   was dropped. Fix: `python exp91\resubmit_banked.py <addr> [...]` (re-claim, one comment line, submit).

## The flag defect (this will bite you)

`pack.json` declares `/MT /Od /Oy- /GS /EHsc /Gy` for a whole region whose real flags are
**`/MT /O2 /GS- /EHsc /Gy`** (93 of 104 `/Od`-labelled open functions screen as optimised).
`/Od` tells: it never inlines `__forceinline`, never emits `and esp,-16` + `[esp+N]` frames, never schedules
x87 (`fmulp st(n)`, `fxch st(n)`), and cannot emit `test byte ptr [eax+ecx],2`.
Check with `python exp91/prologue_probe.py <addr>`. If the label is wrong, compile with
`--flags /MT,/O2,/GS-,/EHsc,/Gy` and follow rule 2.

**`/GS-` is the flag that eats agents (2026-11-13) - but the set is PER FILE, never carry it over.** The wrong set is
wrong on *two or three* axes and the middle one hides the truth. Two units in this region, measured byte-exactly against
their own already-matched neighbours:

| unit | real flags | declared-set result | with `/GS` | with `/GS-` |
|---|---|---|---|---|
| `0x00931eb0`'s (FUN_00925b30 407 B, FUN_0092eaa0 286 B) | **`/MT /O2 /GS- /EHsc /Gy`** | 106 / 357 | 407 / 350 | **407 / 286, byte-identical** |
| `0x00568be0`'s (FUN_00565710 500 B) | **`/MT /O2 /GS /EHsc /Gy`** | 701 | **500, byte-identical** | 489 |

So: **run the oracle on the file you are in.** With a `/GS` set, an agent writes `/O2` code, sees the extent disagree,
and concludes `/O2` is also wrong - because the *other* file needed `/GS-`. **And an `align(16)` local does NOT prove
anything:** at `/Od` it also emits `and esp,-16`, but with `push ebx; mov ebx,esp; ...` and `ebp`-relative slots, versus
optimized `push ebp; mov ebp,esp; and esp,-16; sub esp,N` with `[esp+..]` temporaries. Only a matched neighbour's
**byte-exactness** settles a unit's flags - that is the **flag oracle**: build one matched neighbour under each candidate
set and compare bytes, not sizes.

**A byte-exact match under corrected flags is a WIN, not a report** (§19.93): checkpoint it (after an
`f3check --flags <set>` run that prints MATCH), then `POST /api/v1/flag` with `category: pack_problem`,
**`scope: function`** (never `unit`), `compile_flags: [the full set]`, `checkpoint_id`. The build host recompiles within
~30 min and credits an exact match - **and tries the same set on saved code for every other open function of that file,
so one proof covers the file.**

## Tool traps

5a. **Never regenerate a ledger another tool appends to.** `exp91/closed_list.py` used to WRITE `out/_closed.txt`
   from its own seed plus the lessons file, which silently deleted every entry that `exp91/close_*.py` had
   appended — 116 proved walls became 31 in one command (restored by re-running the close scripts). It now
   **merges**: existing entries win and the script only adds. Same rule for `INDEX.md`/`CLOSED.md`: they are
   generated views; the source of truth is the file the close scripts append to.
5b. **Our `compiler_tips.md` is a SUPERSET of the published one** (2026-11-13, §20.16.1): local 24141 bytes vs the
   site's 23254, and the only difference is an eight-line **TLS** bullet that exists only locally. A blind refresh
   would delete it. Keep `compiler_tips.local.md` (already saved) and **diff after any re-download** — the site's
   copy may be older than ours.
6. **`f3check` refuses to run on a function you currently hold a claim on** unless a plan checkpoint exists.
   It exits 1 and prints **no diff** — which reads as "residue 0" and looks like a free match.
7. **`f3check`'s default diff is truncated.** Counting displayed pairs badly under-reports (a draft ranked 16
   was really 212). Always `--full-diff <file>`.
8. **Plan checkpoints need** separate `FRAME <size> <ebp|esp>` and `REGION R1 0x..-0x..` lines, plus a
   `request_id`. Every check needs `--why`, and `--expect`/`--observed` from the second check on.
9. **`giveup` requires** `category`, `tried`, `still_differs` on work-notes functions. A `400` means the claim
   is **still open**. A `500` is transient — retry (it has succeeded on the second attempt).
10. **`flag` payload:** categories are `index_problem | pack_problem | symbol_problem | checker_problem` —
    **`compile_flags` is rejected**. Flag reports are **per function** (no `scope`), need their own `note`
    saying what is wrong with the data, and need a checkpoint. `keep_claim: false` releases the claim.
11. **`--permute` hangs.** It has cost two claims. Do not use it.
12. **`list_functions` with `exclude_reported: true` returns zero rows** — the pool looks empty and is not.
13. **`[0xe0001000]` in a diff is a display artifact** when `errs = 0`. A `push` shifts `esp`, so
    `[esp+0x10]` vs `[esp+0x14]` can be the same slot — normalise to `ebp`-relative before calling a slot error.

## Cost traps (this is what blew the quota)

14. **Do not hand an agent the 228 KB lessons file.** Grep the section number you need (`§19.41`, `§19.52`, …)
    or read `INDEX.md`.
15. **Input dominates the bill.** A fresh agent re-reads its brief + a unit source + the whole lessons file
    before doing anything. Keep briefs small, point at line ranges, and prefer the in-process batch scorers
    (~0.4 s/compile) over one `f3check` per idea.
16. **2–3 concurrent agents, not 6.** Six long-context agents exhausted a 5-hour quota in about three hours.

## Where things are

* `INDEX.md` — every address ever touched: status, best residue, file, handoff, lesson numbers.
* `out/_index.json` — the same, machine-readable.
* `handoffs/0x<addr>.md` — the ledger per function (residue, dead ends, next levers).
* `handoffs/lessons-rival-code.md` — the full laws; grep by section number.
* `claims/match_<addr>.cpp` — every banked match, re-verifiable.

## Do not hand work away

20. **Do not release a claim you intend to keep working on.** A `giveup` returns the function to the open pool
    *immediately*, and other contributors pick it up — `0x004a21b0` and `0x0090d6b0` both came back "already
    matched" moments after we released them, and `0x00b40790` was matched by someone else the same way. A claim is
    a lease on work we have already paid for (measurements, variants, a classified residue).
21. **When an agent stops, relaunch on the same claim_id** — never release and re-claim. The claim folder, the
    checkpoint, the handoff and the variant dumps all stay attached to that id.
22. **Release only when we are abandoning the function for good** (a proved wall we will not revisit, or a pack
    defect we have reported). Then say so in the handoff so the next session does not reopen it blind.
23. **A held claim with no agent must be relaunched before its lease expires** (Swarm leases are 1 hour). Track
    them: `status` lists `open_claims` with `expires`.

## Before you spend an agent on a near miss

18. **Check `CLOSED.md` first** (machine copy `out/_closed.txt`). A one-instruction residue is not a work item
    until you know the wall behind it has not already been proved. `0x00bd8f90`, `0x007641c0` and `0x0073e740`
    are one wall - the `lea`/sret-slot reservation - named in lessons §13.9 with *"should not spend another hour
    on any of the three"*. Two agents were sent at them anyway because the knowledge was buried in a 228 KB log.
19. **`NEAR_MISSES.md` is filtered against that list.** If an address is not in it, it is matched, closed, or has
    no measured residue. Regenerate with `python exp91\closed_list.py` then `python exp91\build_index.py`.
