"""session_audit.py - what the byte-by-byte work actually cost, from the local OpenCode database.

    python exp91/session_audit.py                 # summary
    python exp91/session_audit.py --csv DIR       # also write per-session and per-model CSVs into DIR

Reads the read-only opencode.db. `session_v2` carries, per session: model (JSON), agent, cost, token counters and
timestamps in epoch milliseconds - `time_created`, `time_busy` (first busy), `time_idle` (when it went idle) - so the wall
clock a session occupied is `time_idle - time_created`. Only counts and timestamps are emitted; no conversation content.
"""
import collections
import datetime
import io
import json
import os
import sqlite3
import sys

DB = os.path.expanduser(r"~\.local\share\opencode\opencode.db")
PROJECT = "C:/f3decomp"


def connect():
    uri = "file:%s?mode=ro" % DB.replace("\\", "/")
    c = sqlite3.connect(uri, uri=True)
    c.row_factory = sqlite3.Row
    return c


def model_of(raw):
    if not raw:
        return "?"
    try:
        j = json.loads(raw)
        name = j.get("id") or j.get("modelID") or ""
        prov = j.get("providerID") or ""
        var = j.get("variant") or ""
        s = "%s/%s" % (prov, name) if prov else name
        return s + ("#" + var if var else "")
    except Exception:
        return str(raw)[:60]


def dur_ms(r):
    end = r["time_idle"] or r["time_updated"] or r["time_created"] or 0
    return max(0, end - (r["time_created"] or end))


def fmt(mins):
    mins = int(mins)
    return "%dh%02dm" % (mins // 60, mins % 60)


def main():
    c = connect()
    cur = c.cursor()
    cur.execute("""SELECT id,parent_id,agent,model,cost,tokens_input,tokens_output,tokens_reasoning,
                          tokens_cache_read,tokens_cache_write,time_created,time_updated,time_idle,
                          title,idle_outcome
                   FROM session_v2 WHERE directory=? ORDER BY time_created""", (PROJECT,))
    rows = [dict(r) for r in cur.fetchall()]
    print("sessions recorded for %s: %d" % (PROJECT, len(rows)))
    if not rows:
        return
    t0, t1 = rows[0]["time_created"], max(r["time_idle"] or r["time_updated"] for r in rows)
    print("window (UTC): %s -> %s" % (datetime.datetime.utcfromtimestamp(t0 / 1000).strftime("%Y-%m-%d %H:%M"),
                                      datetime.datetime.utcfromtimestamp(t1 / 1000).strftime("%Y-%m-%d %H:%M")))
    per = collections.defaultdict(lambda: dict(n=0, mins=0.0, tin=0, tout=0, trea=0, tcr=0, tcw=0, cost=0.0))
    for r in rows:
        m = model_of(r["model"])
        d = per[m]
        d["n"] += 1
        d["mins"] += dur_ms(r) / 60000.0
        d["tin"] += int(r["tokens_input"] or 0)
        d["tout"] += int(r["tokens_output"] or 0)
        d["trea"] += int(r["tokens_reasoning"] or 0)
        d["tcr"] += int(r["tokens_cache_read"] or 0)
        d["tcw"] += int(r["tokens_cache_write"] or 0)
        d["cost"] += float(r["cost"] or 0)
    print("\n%-36s %5s %9s %12s %12s %8s" % ("model", "sess", "wall", "tok_in", "tok_out", "cost$"))
    for m, d in sorted(per.items(), key=lambda kv: -kv[1]["mins"]):
        print("%-36s %5d %9s %12s %12s %8.2f" % (m, d["n"], fmt(d["mins"]),
                                                 "{:,}".format(d["tin"]), "{:,}".format(d["tout"]), d["cost"]))
    tot = sum(d["mins"] for d in per.values())
    print("%-36s %5d %9s %12s %12s %8.2f" % ("TOTAL", len(rows), fmt(tot),
                                             "{:,}".format(sum(d["tin"] for d in per.values())),
                                             "{:,}".format(sum(d["tout"] for d in per.values())),
                                             sum(d["cost"] for d in per.values())))
    print("\nwall clock in the window: %s   sum of session time: %s   concurrency factor: %.1fx"
          % (fmt((t1 - t0) / 60000.0), fmt(tot), tot / max(1.0, (t1 - t0) / 60000.0)))
    print("idle_outcome:", dict(collections.Counter((r["idle_outcome"] or "-") for r in rows)))
    print("agents:", dict(collections.Counter((r["agent"] or "-") for r in rows)))
    days = collections.Counter(datetime.datetime.utcfromtimestamp(r["time_created"] / 1000).strftime("%Y-%m-%d")
                               for r in rows)
    print("sessions per day:", dict(sorted(days.items())))
    dm = collections.defaultdict(float)
    for r in rows:
        dm[datetime.datetime.utcfromtimestamp(r["time_created"] / 1000).strftime("%Y-%m-%d")] += dur_ms(r) / 60000.0
    print("session-minutes per day:", {k: round(v) for k, v in sorted(dm.items())})

    if "--csv" in sys.argv:
        d = sys.argv[sys.argv.index("--csv") + 1]
        os.makedirs(d, exist_ok=True)
        io.open(os.path.join(d, "sessions.csv"), "w", encoding="utf-8", newline="\n").write(
            "session_id,parent_id,agent,model,minutes,cost_usd,tok_in,tok_out,tok_reasoning,"
            "tok_cache_read,tok_cache_write,created_utc,idle_outcome,title\n" +
            "\n".join('%s,%s,%s,%s,%.1f,%.4f,%d,%d,%d,%d,%d,%s,%s,"%s"' % (
                r["id"], r["parent_id"] or "", r["agent"] or "", model_of(r["model"]), dur_ms(r) / 60000.0,
                float(r["cost"] or 0), int(r["tokens_input"] or 0), int(r["tokens_output"] or 0),
                int(r["tokens_reasoning"] or 0), int(r["tokens_cache_read"] or 0),
                int(r["tokens_cache_write"] or 0),
                datetime.datetime.utcfromtimestamp(r["time_created"] / 1000).strftime("%Y-%m-%dT%H:%M"),
                r["idle_outcome"] or "", (r["title"] or "").replace('"', "'")[:120]) for r in rows) + "\n")
        io.open(os.path.join(d, "model-summary.csv"), "w", encoding="utf-8", newline="\n").write(
            "model,sessions,hours,tok_in,tok_out,tok_reasoning,tok_cache_read,tok_cache_write,cost_usd\n" +
            "\n".join("%s,%d,%.2f,%d,%d,%d,%d,%d,%.4f" % (m, d["n"], d["mins"] / 60.0, d["tin"], d["tout"],
                                                         d["trea"], d["tcr"], d["tcw"], d["cost"])
                      for m, d in sorted(per.items(), key=lambda kv: -kv[1]["mins"])) + "\n")
        print("\nwrote sessions.csv + model-summary.csv to", d)


if __name__ == "__main__":
    main()
