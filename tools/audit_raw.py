"""audit_raw.py - hash and cross-check the raw artefacts copied into data/raw/.

    python tools/audit_raw.py <repo-root>

Writes data/raw/manifest.csv (path, bytes, sha256) and data/raw/RAW-AUDIT.md (what each file is, plus the consistency
checks: do the counts in INDEX.md, out/_closed.txt, lessons and sessions.md agree with each other and with data/*.csv?).
"""
import collections
import csv
import hashlib
import io
import os
import re
import sys


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def read(p):
    return io.open(p, encoding="utf-8", errors="replace").read()


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    raw = os.path.join(root, "data", "raw")
    rows = []
    for dirpath, _, files in os.walk(raw):
        for f in sorted(files):
            if f in ("manifest.csv", "RAW-AUDIT.md"):
                continue
            p = os.path.join(dirpath, f)
            rows.append((os.path.relpath(p, root).replace("\\", "/"), os.path.getsize(p), sha(p)))
    with io.open(os.path.join(raw, "manifest.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["path", "bytes", "sha256"])
        w.writerows(rows)

    docs = os.path.join(raw, "docs")
    lessons = read(os.path.join(docs, "lessons-rival-code.md"))
    index = read(os.path.join(docs, "INDEX.md"))
    closed = read(os.path.join(docs, "_closed.txt"))
    sessions = read(os.path.join(docs, "sessions.md"))
    traps = read(os.path.join(docs, "TRAPS.md"))

    n_lessons = len(re.findall(r"(?m)^### ", lessons))
    n_closed = sum(1 for l in closed.splitlines() if "\t" in l)
    n_index_rows = len(re.findall(r"(?m)^\|\s*0x", index))
    statuses = collections.Counter(re.findall(r"\|\s*(MATCHED|CLOSED|claimed|attempted)\s*\|", index))
    n_sess_rows = len(re.findall(r"(?m)^\|[^|]*\|\s*0x", sessions))
    n_handoffs = len([f for f in os.listdir(os.path.join(raw, "handoffs")) if f.startswith("0x")])
    n_tools = len(os.listdir(os.path.join(raw, "tools")))
    cand = len(os.listdir(os.path.join(root, "candidates"))) if os.path.isdir(os.path.join(root, "candidates")) else 0

    def count_csv(name):
        p = os.path.join(root, "data", name)
        if not os.path.exists(p):
            return None
        return sum(1 for _ in io.open(p, encoding="utf-8")) - 1

    summ = None
    p = os.path.join(root, "data", "model-summary.csv")
    if os.path.exists(p):
        with io.open(p, encoding="utf-8") as fh:
            summ = list(csv.DictReader(fh))

    lines = []
    lines.append("# Raw artefact audit\n")
    lines.append("Hashes and cross-checks for everything in `data/raw/`. Regenerate with\n"
                 "`python tools/audit_raw.py .`; the machine list is `data/raw/manifest.csv`.\n")
    lines.append("## Files\n")
    lines.append("| path | bytes | sha256 (first 16) | what it is |")
    lines.append("|---|---|---|---|")
    desc = {
        "sessions.md": "the subagent registry: one row per launch, with session id, claim, model, purpose, status, outcome",
        "lessons-rival-code.md": "the law book - every lever and wall with the measurement behind it",
        "INDEX.md": "every address touched: status, best residue, file, handoff",
        "CLOSED.md": "the proved walls, human view",
        "_closed.txt": "the same walls, machine copy (address<TAB>reason)",
        "NEAR_MISSES.md": "open near misses at residue <= 10",
        "TRAPS.md": "strike risks, tool traps, cost traps",
        "AGENT_UPDATE_2026-11-13.md": "the brief handed to every agent (includes two refuted laws)",
        "SESSION_CLOSE_6_2026-11-13.md": "state + strategy ledger, evening",
        "SESSION_CLOSE_7_2026-11-13.md": "state + strategy ledger, night (the twin strategy)",
        "LOCAL_MODEL_TASK_0x00501250.md": "self-contained task for a local model",
        "_twin_candidates.json": "open twin-bearing candidates, with confidence and give-up counts",
        "_big_twin_pool.json": "the big (>=1 KB) twin pool as scanned",
    }
    for path, size, h in rows:
        base = os.path.basename(path)
        what = desc.get(base, "handoff for one function: what was tried, what it leaves behind" if "/handoffs/" in path
                        else "analysis tool" if "/tools/" in path else "")
        lines.append("| `%s` | %d | `%s` | %s |" % (path, size, h[:16], what))
    lines.append("")
    lines.append("## Consistency checks\n")
    lines.append("| quantity | value | source |")
    lines.append("|---|---|---|")
    lines.append("| addresses in INDEX.md | %d | `docs/INDEX.md` |" % n_index_rows)
    lines.append("| INDEX status counts | %s | `docs/INDEX.md` |" % dict(statuses))
    lines.append("| proved walls | %d | `docs/_closed.txt` |" % n_closed)
    lines.append("| law sections | %d | `docs/lessons-rival-code.md` |" % n_lessons)
    lines.append("| session registry rows | %d | `docs/sessions.md` |" % n_sess_rows)
    lines.append("| handoff files | %d | `docs/handoffs/` |" % n_handoffs)
    lines.append("| analysis tools | %d | `docs/tools/` |" % n_tools)
    lines.append("| candidate files | %d | `candidates/` |" % cand)
    lines.append("| sessions in sessions.csv | %s | `data/sessions.csv` |" % count_csv("sessions.csv"))
    lines.append("| models in model-summary.csv | %s | `data/model-summary.csv` |" % (len(summ) if summ else None))
    lines.append("")
    if summ:
        tot_mins = sum(float(r["hours"]) * 60 for r in summ)
        tot_sess = sum(int(r["sessions"]) for r in summ)
        lines.append("## What the audit says\n")
        lines.append("* **%d sessions** in the project directory, totalling **%.0f hours of session wall-clock** "
                     "(sum of session lifetimes - sessions overlap, so this is concurrency, not elapsed time)."
                     % (tot_sess, tot_mins / 60.0))
        top = sorted(summ, key=lambda r: -float(r["hours"]))[:3]
        for r in top:
            lines.append("* `%s` - %s sessions, %.1f h, %s tokens in / %s out"
                         % (r["model"], r["sessions"], float(r["hours"]),
                            "{:,}".format(int(r["tok_in"])), "{:,}".format(int(r["tok_out"]))))
        lines.append("* Cost recorded by the harness is **$0.00** for every model: the work ran on subscription-style "
                     "accounts (`opencode-go`), so the real constraint was never money - it was **quota windows** and "
                     "**leases**.\n")
    lines.append("## What was deliberately left out\n")
    lines.append("No game binary, no `.obj`, no build output and no credential. The files under `data/raw/` are the working "
                 "record: our own drafts, measurements and analysis. Other contributors' attempts are referred to by "
                 "checkpoint id and score; where an instruction or two is quoted it is for comparison, not as a source.\n")
    io.open(os.path.join(raw, "RAW-AUDIT.md"), "w", encoding="utf-8", newline="\n").write("\n".join(lines))
    print("wrote data/raw/manifest.csv (%d files) and data/raw/RAW-AUDIT.md" % len(rows))
    print("INDEX rows %d | walls %d | laws %d | session rows %d | handoffs %d | candidates %d"
          % (n_index_rows, n_closed, n_lessons, n_sess_rows, n_handoffs, cand))
    print("statuses:", dict(statuses))


if __name__ == "__main__":
    main()
