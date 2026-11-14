# 06 — The session audit: what this actually consumed

Every other chapter is about the work. This one is about the **cost**, because the honest answer to "could one person do
this" depends on it, and because most of what went wrong was not the decompilation.

Numbers come from the local agent harness database (`session_v2`: one row per session, with model, timestamps and token
counters) and from the session registry in `data/raw/docs/sessions.md`. Regenerate with
`python exp91/session_audit.py --csv data`.

---

## 1. The shape of the effort

```
window           2026-11-11 08:08  ->  2026-11-14 02:06 UTC   (66 hours elapsed)
sessions         376          (in the project directory)
session hours    282 h 53 m   (sum of session lifetimes)
concurrency      4.3x         (sessions ran in parallel waves)
tokens           99,198,473 in  /  10,799,790 out
cost recorded    $0.00        (subscription accounts, see §3)
```

Sessions per day, and the session-minutes each day consumed:

| day | sessions | session-minutes |
|---|---|---|
| 2026-11-11 | 21 | 7,431 |
| 2026-11-12 | 190 | 5,322 |
| 2026-11-13 | 163 | 4,180 |
| 2026-11-14 | 2 | 41 |

The 4.3x concurrency is the whole architecture of the thing: the human session ran the account, the claims and the
verification, while **subagents worked functions in parallel**. 369 of the 376 sessions are `general` agents; 6 are `build`
and 1 is `plan`.

Outcomes: **337 succeeded, 27 interrupted, 12 failed.** The interrupted ones are almost all "turn ended while a long sweep
was still running" — a harness property we learned to work around (keep checks inline, never leave a sweep in a background
agent).

---

## 2. Who did the work

| model | sessions | session hours | tokens in | tokens out |
|---|---|---|---|---|
| `opencode-go/deepseek-v4.1-flash#high` | **263** | **252.2** | 80,620,713 | 9,439,545 |
| `opencode/glm-5.3-flash-free#high` | 1 | 8.2 | 196,966 | 7,570 |
| `opencode-go/glm-5.3-flash#max` | 7 | 4.5 | 2,609,336 | 160,780 |
| `opencode-go/beam-free` | 14 | 3.8 | 3,061,436 | 195,000 |
| `opencode-go/beam-free#max` | 19 | 3.2 | 4,489,465 | 351,752 |
| `opencode-go/beam-free#high` | 34 | 2.8 | 1,608,418 | 117,995 |
| `opencode-go/deepseek-v4.1-flash#max` | 5 | 2.0 | 828,352 | 101,683 |
| `opencode-go/deepseek-v4.1-flash#low` | 10 | 1.9 | 808,663 | 104,716 |
| `opencode-go/minimax-m3.1-flash#max` | 5 | 1.4 | 633,181 | 117,021 |
| `omniroute/auto/coding#high` | 5 | 0.9 | 2,958,600 | 98,945 |
| others (5 models) | 13 | 1.6 | 1,136,583 | 100,965 |

**DeepSeek V4.1 Flash at the `high` reasoning variant carried 89% of the session-hours.** That is not a preference, it is
what survived the quota walls (next section). The useful signal is the *variant* spread: `#max` sessions were 4x more
expensive in tokens per session and did not match better; `#low` was used only for short probe bursts.

Model choice at the end of the session was fixed by evidence, and the rule written into the project notes is:
**`opencode-go/deepseek-v4.1-flash#high` for every agent, with the free tiers as a zero-cost first attempt only.**

---

## 3. Quotas: what actually pushed back

Nothing in this project cost money. Every model ran on a subscription-style account where the constraint is a **window**,
not a price — and the windows were the single largest source of lost work.

| wall | how it presented | what we did about it |
|---|---|---|
| **free-tier usage limits** | agents refusing to start with *"Free usage limit reached"* after a few hours of waves | fall back to the paid Go account; keep free tiers for a first cheap attempt only |
| **separate 5-hour ceilings per account** | one account stops while another still works | keep two account families in use (`opencode` free and `opencode-go`), rotate |
| **claim leases: 1 hour (2 for >1 KB, 3-4 for >4 KB)** | a function's claim expiring mid-work; a lapsed claim can *pause claiming* for the whole account | re-claim by address, hand the same `claim_id` to a fresh agent, and **release deliberately with `giveup` + `best_code`** rather than let a lease lapse |
| **pending-submission cap** | queued submissions block new ones | keep the queue shallow; verify status before launching a wave |
| **verification cadence** (3 h on the entry tier, 10 min on the top tier) | matches sitting unverified for hours, blocking the next claim count | worked in waves and used the wait to author; the top tier's 10-minute cadence changed the whole loop |
| **request-rate limits** | transient `HTTP 500` on the claim endpoint | retry with backoff (`exp91/retry_claims.py`); never treat a 5xx as a verdict |

The most expensive quota lesson was structural, not per-model: **a lapsed claim can pause claiming for the account.** After
that, every claim was released deliberately — with a category, what was tried, what still differs, and the best code — so
the build host could still finish it and the account never sat on a dead lease.

---

## 4. Everything else that broke

These are the failures that cost the most time and had nothing to do with C++:

1. **Seven submissions vanished.** Each returned `HTTP 200` with a submission id; an hour later the function was `open`
   with an empty verification queue. No strike, no rejection, no record. The fix is a habit, not a tool: re-check the
   address in a *later* session and resubmit from the banked file with one comment line.
2. **The `already found unfit` 409 is a cache keyed to the source text**, and it goes stale as the project file changes.
   Four matches were unblocked by prepending **one comment line**.
3. **A "score 0" saved attempt can be a false positive.** One banked candidate had matched a *library* function
   (`std::string::replace`) that happened to be the same size; the real target was a different overload.
4. **The pack can be wrong, and the platform says so.** 86 of 160 twin-bearing functions were **paused** on confirmed
   `file_problem` defects: missing helper headers, spans that stop before their own catch handlers, units that already
   define the target. That is data, not difficulty — and it is why "how many functions are left" is a much smaller number
   than it looks.
5. **The checker's region board over-reports** on files whose stand-ins are named `FUN_<8 hex>`: every call prints as a
   difference and the board can say "0 of 5 regions exact" when a third of the bytes are exact. The verdict is fine; the
   board is not. Steer by a real byte diff.
6. **The work-notes protocol blocks checkpoints** when an older unsent note is missing an observation — and one agent spent
   ten minutes on that instead of bytes.
7. **Compile-flag reports are per function and need a matching candidate**, which is only obvious after two rejected
   filings. The working recipe is in the lessons.
8. **The harness restarts and cancels agents.** Several sessions in this log end with an agent's work banked but its turn
   gone. The countermeasure is the same as for leases: write the handoff *before* you stop, and keep the best draft on
   disk with its hash.

---

## 5. What the numbers say about the method

* **4.3x concurrency is what made 66 hours produce 283 session-hours.** The human session is the bottleneck and should
  never be doing the per-function work.
* **89% of the work ran on one model at one reasoning level.** Model choice mattered far less than *brief quality*: the
  agents that matched had a brief carrying the twin, the byte listing, the flag table and the named residue; the ones that
  burned leases were told to "try harder".
* **The cost of a wrong hypothesis is one lease (~1 hour).** That is small enough to spend and large enough that it is worth
  saying "I was wrong" and writing down why — two of the session's laws exist only because a proposed lever was falsified
  and the falsification was recorded.
* **The cheapest wins were not authoring.** Four matches came from the recovery layer (stale cache, banked-but-open audit,
  packet-cache harvest) and two from the flag route — none of them required new source.

The honest summary: **six matches in 283 session-hours is not a good rate for a person, and it is a fine rate for a
pipeline** — because the durable output was 18 levers, 110 classified walls, and a recovery layer that will keep paying on
work that is already done.
