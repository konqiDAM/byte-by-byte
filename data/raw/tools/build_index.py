"""build_index.py - one index of every address we have touched.

    python exp91/build_index.py

Writes INDEX.md (human) and out/_index.json (machine). Sources, in priority order:

  claims/match_<addr>.cpp        -> MATCHED
  handoffs/0x<addr>.md           -> attempted, with the handoff
  out/<addr>/                    -> attempted, artefacts only
  claims/<clm>/pack.json         -> claimed at least once (address recorded)
  rivals/<addr>/                 -> rival draft on disk

Best residue comes from out/_true_ranking.json / _probe_more.json when present, else from the first
"ndiff N" / "residue N" in the handoff. Lessons section numbers are attached by scanning the lessons file
for the address.
"""
import glob
import io
import json
import os
import re

ROOT = r"C:\f3decomp"
LESSONS = os.path.join(ROOT, "handoffs", "lessons-rival-code.md")


def addr_of(path):
    base = os.path.basename(path)
    return "0x" + base[6:14].lower() if base.startswith("match_") and base.endswith(".cpp") else None


def main():
    idx = {}
    closed = {}
    cf = os.path.join(ROOT, "out", "_closed.txt")
    if os.path.exists(cf):
        for ln in io.open(cf, encoding="utf-8").read().splitlines():
            if "\t" in ln:
                a, why = ln.split("\t", 1)
                closed[a.strip()] = why.strip()

    def row(a):
        return idx.setdefault(a, {"address": a, "size": None, "status": "claimed",
                                  "best": None, "file": None, "handoff": None,
                                  "lessons": [], "artefacts": 0})

    # matches
    for p in glob.glob(os.path.join(ROOT, "claims", "match_*.cpp")):
        a = addr_of(p)
        if a:
            r = row(a)
            r["status"] = "MATCHED"
            r["file"] = os.path.relpath(p, ROOT)
            r["size"] = os.path.getsize(p) and r["size"]

    # claim packs give address + size + flags
    for p in glob.glob(os.path.join(ROOT, "claims", "*", "pack.json")):
        try:
            d = json.load(open(p))
        except Exception:
            continue
        a = d.get("address")
        if not a:
            continue
        a = "0x" + str(a).lower().replace("0x", "")
        r = row(a)
        r["size"] = d.get("size") or r["size"]
        r["flags"] = d.get("flags")
        d2 = os.path.dirname(p)
        for f in glob.glob(os.path.join(d2, "cand*.cpp")):
            if r["file"] is None:
                r["file"] = os.path.relpath(f, ROOT)
            r["artefacts"] += 1

    # handoffs
    for p in glob.glob(os.path.join(ROOT, "handoffs", "0x*.md")):
        a = os.path.basename(p)[:10].lower()
        r = row(a)
        r["handoff"] = os.path.relpath(p, ROOT)
        if r["status"] == "claimed":
            r["status"] = "attempted"
        try:
            txt = io.open(p, encoding="utf-8", errors="replace").read(4000)
        except Exception:
            txt = ""
        m = re.search(r"ndiff\D{0,6}(\d+)", txt) or re.search(r"residue\D{0,6}(\d+)", txt)
        if m and int(m.group(1)) > 0 and (r["best"] is None or int(m.group(1)) < r["best"]):
            r["best"] = int(m.group(1))

    # out/ artefacts
    for d in glob.glob(os.path.join(ROOT, "out", "*")):
        n = os.path.basename(d)
        if len(n) == 8 and re.fullmatch(r"[0-9a-fA-F]{8}", n):
            r = row("0x" + n.lower())
            r["artefacts"] += len(glob.glob(os.path.join(d, "**", "*.cpp"), recursive=True))
            if r["status"] == "claimed":
                r["status"] = "attempted"

    # probe rankings give the true residue of a shipped draft
    for f in ("_true_ranking.json", "_probe_more.json"):
        p = os.path.join(ROOT, "out", f)
        if not os.path.exists(p):
            continue
        try:
            for x in json.load(open(p)):
                a = x.get("address")
                if not a:
                    continue
                r = row(a)
                nd = x.get("residue")
                if nd is None and x.get("best"):
                    nd = x["best"][1]
                    # nd == 0 without a match means "no diff lines produced" (compile error or a
                    # truncated/refused check), NOT a clean bill. The truncated-diff bug again.
                    if nd == 0:
                        nd = None
                if isinstance(nd, int) and nd > 0 and (r["best"] is None or nd < r["best"]):
                    r["best"] = nd
        except Exception:
            pass

    # lessons cross-reference
    if os.path.exists(LESSONS):
        txt = io.open(LESSONS, encoding="utf-8", errors="replace").read()
        for a in idx:
            s = a[2:]
            if s in txt.lower():
                for m in re.finditer(r"(?:###|####)\s+(1[89]\.\d+(?:\.\d+)?)[^\n]*\n(?:[^\n]*\n){0,12}?",
                                     txt):
                    if a[2:] in m.group(0).lower():
                        idx[a]["lessons"].append(m.group(1))
                idx[a]["lessons"] = sorted(set(idx[a]["lessons"]))[:4]

    rows = sorted(idx.values(), key=lambda r: (r["status"] != "MATCHED", r["best"] if r["best"] is not None else 9999))
    ext = os.path.join(ROOT, "out", "_matched_external.txt")
    external = set()
    if os.path.exists(ext):
        external = {l.strip() for l in io.open(ext, encoding="utf-8") if l.strip()}
    for r in rows:
        if r["address"] in external:
            r["status"] = "MATCHED"
            r["file"] = r["file"] or "(matched with someone else's candidate or the host solver)"
            continue
        if r["status"] != "MATCHED" and r["address"] in closed:
            r["status"] = "CLOSED"
            r["why_closed"] = closed[r["address"]]
    json.dump(rows, open(os.path.join(ROOT, "out", "_index.json"), "w"), indent=1)

    md = ["# INDEX - every address this project has touched", "",
          "Generated by `python exp91/build_index.py`. Machine copy: `out/_index.json`.", "",
          "| address | size | status | best | file | handoff | lessons |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        md.append("| %s | %s | %s | %s | %s | %s | %s |" % (
            r["address"], r["size"] or "", r["status"],
            "" if r["best"] is None else r["best"],
            r["file"] or "", (r["handoff"] or "").replace("handoffs\\", ""),
            ",".join(r["lessons"])))
    io.open(os.path.join(ROOT, "INDEX.md"), "w", encoding="utf-8", newline="\n").write("\n".join(md) + "\n")

    counts = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1

    # the worklist that matters: unmatched addresses with a known small residue
    near = [r for r in rows if r["status"] not in ("MATCHED", "CLOSED")
            and r["best"] is not None and r["best"] <= 10]
    near.sort(key=lambda r: (r["best"], r["size"] or 0))
    md = ["# NEAR MISSES - open addresses with a known residue <= 10", "",
          "Generated by `python exp91/build_index.py`. Work from the top; re-measure before trusting a row",
          "(`f3check --pack ... --full-diff`), because a residue can be stale and a truncated diff under-reports.", "",
          "| best | address | size | file | handoff |", "|---|---|---|---|---|"]
    for r in near:
        md.append("| %s | %s | %s | %s | %s |" % (r["best"], r["address"], r["size"] or "",
                                                  (r["file"] or "").replace("claims\\", ""),
                                                  (r["handoff"] or "").replace("handoffs\\", "")))
    io.open(os.path.join(ROOT, "NEAR_MISSES.md"), "w", encoding="utf-8", newline="\n").write(
        "\n".join(md) + "\n")
    print("INDEX.md: %d addresses  %s" % (len(rows), counts))
    print("matched:", sum(1 for r in rows if r["status"] == "MATCHED"))
    near = [r for r in rows if r["status"] not in ("MATCHED", "CLOSED")
            and r["best"] is not None and r["best"] <= 5]
    print("near misses (<=5) still open:", len(near))
    for r in near[:12]:
        print("   %-12s size %-5s best %-3s %s" % (r["address"], r["size"] or "?",
                                                   r["best"], r["file"] or r["handoff"] or ""))


if __name__ == "__main__":
    main()
