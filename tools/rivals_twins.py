"""Find and document FNV twins for everything the harvest holds.

    python exp91\\rivals_twins.py            # analyse, write the registries + rivals\\_twins.md
    python exp91\\rivals_twins.py --dry      # analyse only, write nothing

A twin is the FNV decomp function with the same original source. It is worth more than any
draft: a draft is somebody's guess, a twin is ~40 lines you can read and port. Four sources,
strongest first - a lower source never overwrites a higher one:

  exact    the pack's own symbol already names an FNV function (mangled symbol match)
  matcher  f3twins' weighted candidate list (twins\\cache\\twins.json), high/medium only
  name     a qualified name asserted in a contributor's note, kept only under four strict
           filters, because the naive version is ~90 % noise
  unit     the pack's unit_*.cpp identifies the original file: when the functions of one unit
           agree on a single FNV file, that file is known, so every other function of the unit
           has its twin among that file's ~50 functions

Writes:
  rivals\\_twins.md            what an agent reads
  rivals\\_twin_by_unit.json   unit -> FNV file, the anchors that proved it, the file's functions
  rivals\\_twin_by_name.json   name -> FNV entry, with agrees | new | differs against the matcher
  rivals\\<address>\\index.json gets twin_fnv / twin_name / twin_source / twin_from / twin_conf
"""
import argparse
import glob
import hashlib
import json
import os
import pickle
import re
import sys
from collections import Counter, defaultdict

ROOT = r"C:\f3decomp"
RIVALS = os.path.join(ROOT, "rivals")
TWINS = os.path.join(ROOT, "twins", "cache")
TWINS_JSON = os.path.join(TWINS, "twins.json")
FNV_PKL = os.path.join(TWINS, "fnv_index.pkl")
OUT_MD = os.path.join(RIVALS, "_twins.md")
OUT_UNIT = os.path.join(RIVALS, "_twin_by_unit.json")
OUT_NAME = os.path.join(RIVALS, "_twin_by_name.json")

CONF_RANK = {"high": 0, "medium": 1, "low": 2}
# a candidate pointing into these files is not a real location in the game's source
PSEUDO_SRC = ("src/staging/", "blk_")
# ranges whose functions cannot match (index spans end at the catch funclets) - a unit that
# lives there is identified but still not workable, and must not be handed out as a lead
DEAD_RANGES = [(0x00BA0000, 0x00C40000)]


def dead(addr):
    a = int(addr, 16)
    return any(lo <= a <= hi for lo, hi in DEAD_RANGES)

NAME_RE = re.compile(r"\b([A-Z][A-Za-z0-9_]{2,}::[A-Za-z_~][A-Za-z0-9_]{2,})\b"
                     r"|\b(hkp?[A-Z][A-Za-z0-9]+_[a-zA-Z][A-Za-z0-9_]+)\b")


def load(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def out(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)


def eaddr(e):
    """The index stores the address as an int; older dumps store hex text."""
    a = e.get("addr")
    return a if isinstance(a, int) else int(str(a), 16)


def load_fnv():
    entries = pickle.load(open(FNV_PKL, "rb"))
    by_addr, by_name, by_src, by_sym = {}, defaultdict(list), defaultdict(list), {}
    for e in entries:
        try:
            a = eaddr(e)
        except Exception:
            continue
        by_addr[a] = e
        by_name[e.get("name") or ""].append(e)
        by_src[e.get("src") or ""].append(e)
        if e.get("symbol"):
            by_sym[e["symbol"]] = e
    for v in by_src.values():
        v.sort(key=lambda e: int(e.get("line") or 0))
    return by_addr, by_name, by_src, by_sym


def unit_key(pack):
    """The unit a pack belongs to, by content: several functions share one unit_*.cpp."""
    if not pack:
        return None
    paths = glob.glob(os.path.join(pack, "unit_*.cpp"))
    if not paths:
        return None
    h = hashlib.sha256()
    for p in sorted(paths):
        h.update(open(p, "rb").read())
    return h.hexdigest()[:12]


def best_twin(cands):
    """Highest-confidence candidate; None when the only options are 'low' or pseudo-files."""
    strong = [c for c in cands if c.get("conf") in ("high", "medium")
              and not any(s in (c.get("src") or "") for s in PSEUDO_SRC)]
    if not strong:
        return None
    strong.sort(key=lambda c: (CONF_RANK[c["conf"]], -float(c.get("score") or 0)))
    return strong[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--no-stamp", action="store_true",
                    help="write the registries and the document, but leave index.json alone "
                         "(use while another scoring pass is writing them)")
    ap.add_argument("--max-name-uses", type=int, default=2,
                    help="keep a name only when at most N harvested addresses use it")
    ap.add_argument("--max-index-hits", type=int, default=2,
                    help="keep a name only when at most N FNV entries share it")
    args = ap.parse_args()

    cands_all = load(TWINS_JSON, {})
    fnv, fnv_by_name, fnv_by_src, fnv_by_sym = load_fnv()
    infos = {}
    for p in glob.glob(os.path.join(RIVALS, "0x*", "index.json")):
        d = load(p, {})
        a = (d.get("address") or os.path.basename(os.path.dirname(p))).lower()
        infos[a] = d
    print("addresses %d | f3twins candidates %d | fnv functions %d"
          % (len(infos), len(cands_all), len(fnv)))

    # ---- 0. exact: the pack's own symbol already names an FNV function -------------
    exact = {}
    for a, info in infos.items():
        pack = info.get("pack")
        if not pack:
            continue
        sym = (load(os.path.join(pack, "pack.json"), {}) or {}).get("symbol") or ""
        if not sym or sym.startswith("FUN_"):
            continue
        e = fnv_by_sym.get(sym) or (fnv_by_name.get(sym) or [None])[0]
        if e:
            exact[a] = e
    print("exact twins (pack symbol -> FNV symbol): %d" % len(exact))

    # ---- 1. the matcher, per address ------------------------------------------------
    matched, conf_count = {}, Counter()
    for a in infos:
        top = best_twin(cands_all.get(a) or [])
        if top:
            matched[a] = top
            conf_count[top["conf"]] += 1
    print("matcher twins (high/medium): %d  (%s)" % (len(matched), dict(conf_count)))

    # ---- 2. unit -> FNV file, by the vote of the unit's own functions ---------------
    unit_of, unit_members = {}, defaultdict(list)
    for a, info in infos.items():
        k = unit_key(info.get("pack"))
        if k:
            unit_of[a] = k
            unit_members[k].append(a)
    print("units: %d, holding %d addresses" % (len(unit_members), len(unit_of)))

    by_unit, resolved = {}, {}
    for k, members in unit_members.items():
        votes = Counter()
        anchors = defaultdict(list)
        for a in members:
            # rank-weighted support: the true file tends to appear *somewhere* in the list of
            # every function of the unit, even when a neighbour's guess sits at rank 1
            seen_src, rank = set(), 0
            for c in cands_all.get(a) or []:
                src = c.get("src") or ""
                if not src or any(s in src for s in PSEUDO_SRC) or src in seen_src:
                    continue
                seen_src.add(src)
                rank += 1
                if rank > 4:
                    break
                w = {1: 4, 2: 3, 3: 2, 4: 1}[rank]
                votes[src] += w
                if a not in anchors[src]:
                    anchors[src].append(a)
            e = exact.get(a)                       # an exact twin outvotes any guess
            if e and e.get("src"):
                votes[e["src"]] += 6
        if not votes:
            continue
        ranked = votes.most_common()
        src, n = ranked[0]
        second = ranked[1][1] if len(ranked) > 1 else 0
        entry = {"fnv_file": src, "anchors": anchors[src], "votes": dict(votes),
                 "members": len(members),
                 # a plurality with a clear margin, not a majority
                 "confident": n >= 2 and n >= 2 * max(second, 1),
                 "functions_in_file": [
                     {"fnv": "0x%08x" % eaddr(e), "name": e.get("name"),
                      "scope": e.get("scope"), "size": int(e.get("size") or 0),
                      "line": int(e.get("line") or 0)}
                     for e in fnv_by_src.get(src, [])
                 ]}
        by_unit[k] = entry
        if entry["confident"]:
            resolved[k] = entry
    print("units with an anchored FNV file: %d (confident: %d, covering %d addresses)"
          % (len(by_unit), len(resolved),
             sum(len(unit_members[k]) for k in resolved)))

    # ---- 3. names asserted in notes, four strict filters ---------------------------
    note_names = defaultdict(set)
    for a, info in infos.items():
        for c in info.get("checkpoints") or []:
            for m in NAME_RE.finditer(c.get("note") or ""):
                note_names[next(g for g in m.groups() if g)].add(a)
    by_name = {}
    for name, addrs in note_names.items():
        if len(addrs) > args.max_name_uses:
            continue
        hits = fnv_by_name.get(name) or fnv_by_name.get(name.split("::")[-1]) or []
        if not hits or len(hits) > args.max_index_hits:
            continue
        e = hits[0]
        fnv_addr = "0x%08x" % eaddr(e)
        for a in sorted(addrs):
            t = matched.get(a) or {}
            verdict = "new" if not t else ("agrees" if (t.get("fnv") or "").lower() == fnv_addr
                                           else "differs")
            by_name[a] = {"name": name, "fnv": fnv_addr, "fnv_file": e.get("src"),
                          "line": e.get("line"), "fnv_size": int(e.get("size") or 0),
                          "verdict": verdict, "matcher": t.get("fnv")}
    print("name twins (4 filters): %d addresses, verdicts %s"
          % (len(by_name), dict(Counter(v["verdict"] for v in by_name.values()))))

    # ---- 4. one twin per address: exact > matcher > name ---------------------------
    def twin_row(a):
        e = exact.get(a)
        if e:
            return {"fnv": "0x%08x" % eaddr(e), "name": e.get("name"), "src": e.get("src"),
                    "line": e.get("line"), "conf": "exact", "from": "exact"}
        t = matched.get(a)
        if t:
            return {"fnv": t["fnv"], "name": t.get("name"), "src": t.get("src"),
                    "line": t.get("line"), "conf": t["conf"], "from": "matcher"}
        n = by_name.get(a)
        if n and n["verdict"] in ("agrees", "new"):
            return {"fnv": n["fnv"], "name": n["name"], "src": n["fnv_file"],
                    "line": n["line"], "conf": "name", "from": "name"}
        return None

    stamped = 0
    for a, info in infos.items():
        t = twin_row(a)
        if t:
            info["twin_fnv"] = t["fnv"]
            info["twin_name"] = t.get("name")
            info["twin_source"] = "%s:%s" % (t.get("src"), t.get("line"))
            info["twin_from"] = t["from"]
            info["twin_conf"] = t["conf"]
        k = unit_of.get(a)
        if k in resolved:
            info["twin_unit_file"] = resolved[k]["fnv_file"]
        if any(x.startswith("twin") for x in info):
            stamped += 1
            if not args.dry and not args.no_stamp:
                out(os.path.join(RIVALS, a, "index.json"), info)
    print("addresses stamped with a twin: %d" % stamped)
    if args.dry:
        return

    out(OUT_UNIT, by_unit)
    out(OUT_NAME, by_name)

    # ---- 5. the document the other agent reads -----------------------------------
    leads = []
    for a, info in infos.items():
        b = info.get("best") or {}
        size = info.get("size") or 0
        usable = (b.get("ndiff") is not None and not (b.get("errs") or 0)
                  and b.get("extent") == size)
        leads.append({"addr": a, "ndiff": b.get("ndiff"), "size": size, "usable": usable,
                      "twin": twin_row(a),
                      "unit": (resolved.get(unit_of.get(a)) or {}).get("fnv_file")})
    leads.sort(key=lambda r: (r["ndiff"] if r["ndiff"] is not None else 9999,
                              not r["usable"], r["size"]))
    with_twin = [r for r in leads if r["twin"] or r["unit"]]
    lines = ["# Twins for the harvested pool - %d addresses" % len(infos), "",
             "A twin is the Fallout New Vegas decomp function with the same original source:",
             "`file:line` you can read and port, instead of guessing from a rival draft.",
             "Generated by `python exp91\\rivals_twins.py` (offline, 0 API requests).", "",
             "| what | count |", "|---|---|",
             "| addresses with an **exact** twin (pack symbol -> FNV symbol) | %d |" % len(exact),
             "| addresses with a matcher twin (high/medium) | %d |" % len(matched),
             "| of those, high confidence | %d |" % conf_count["high"],
             "| units with a confidently resolved FNV file | %d of %d |"
             % (len(resolved), len(unit_members)),
             "| name twins surviving the four filters | %d |" % len(by_name),
             "| addresses with any twin at all | %d |" % len(with_twin), "",
             "Sources, strongest first: `exact` (the pack's own symbol names an FNV function),",
             "`matcher` (f3twins weighted candidates), `name` (a contributor's note, filtered),",
             "`unit` (the whole file is known, so the twin is one of its functions).", "",
             "## Usable drafts that carry a twin (the cheapest work in the pool)", "",
             "Bold = the draft already compiles clean at the original's exact size, so the twin",
             "plus that draft is a submission waiting for someone to align the last bytes.", "",
             "| ndiff | function | size | twin | file:line | from |",
             "|---|---|---|---|---|---|"]
    strong = [x for x in leads if (x["twin"] or x["unit"]) and x["usable"]]
    for r in strong[:40]:
        t = r["twin"] or {}
        lines.append("| **%s** | `%s` | %d | %s | %s | %s |"
                     % (r["ndiff"], r["addr"], r["size"], t.get("name") or "-",
                        ("%s:%s" % (t.get("src"), t.get("line"))) if t else
                        ("%s (unit: one of its functions)" % r["unit"] if r["unit"] else "-"),
                        (t.get("from") or "unit")))
    if not strong:
        lines.append("| - | - | - | none | - | - |")
    lines += ["", "%d of the %d usable drafts carry a twin; the rest have only a rival draft."
              % (len(strong), len([x for x in leads if x["usable"]])), "",
              "## The closest drafts, with or without a twin", "",
              "| ndiff | function | size | twin | file:line | from |",
              "|---|---|---|---|---|---|"]
    for r in [x for x in leads if x["ndiff"] is not None and x["ndiff"] <= 3]:
        t = r["twin"] or {}
        lines.append("| %s%s%s | `%s` | %d | %s | %s | %s |"
                     % ("**" if r["usable"] else "", r["ndiff"],
                        "**" if r["usable"] else "", r["addr"], r["size"],
                        t.get("name") or "-",
                        ("%s:%s" % (t.get("src"), t.get("line"))) if t else "-",
                        (t.get("from") or "-") + ("/unit" if r["unit"] else "")))
    lines += ["", "## Units whose original file is known (%d)" % len(resolved), "",
              "Every function of a resolved unit lives in that file, so its twin is one of the",
              "file's functions listed in `rivals\\_twin_by_unit.json`. That turns 11 000",
              "candidates into ~50 you can read.", "",
              "| FNV file | anchors | members | still open | note |", "|---|---|---|---|---|"]
    for k, e in sorted(resolved.items(),
                       key=lambda kv: (-sum(not dead(a) for a in unit_members[kv[0]]),
                                       -len(kv[1]["anchors"]))):
        mem = unit_members[k]
        alive = [a for a in mem if not dead(a)]
        open_members = [a for a in alive
                        if not (exact.get(a) or matched.get(a) or by_name.get(a))]
        note = "dead range - identified, not workable" if not alive else (
            "%d dead-range members" % (len(mem) - len(alive)) if len(alive) < len(mem) else "")
        lines.append("| `%s` | %d (%s) | %d | %d | %s |"
                     % (e["fnv_file"], len(e["anchors"]),
                        ", ".join("`%s`" % a for a in e["anchors"][:3]),
                        len(mem), len(open_members), note))
    lines += ["", "## Where to start", "",
              "1. the ndiff 1-2 rows above that carry a twin: port the twin, submit on MATCH;",
              "2. then the resolved units, biggest anchor count first;",
              "3. `rivals\\_twin_by_name.json` last - `differs` is a lead, never a fact.", "",
              "A twin is a starting point, not a match: the checker verifies bytes, the twin",
              "only says what the original source looked like."]
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote %s\n      %s\n      %s" % (OUT_MD, OUT_UNIT, OUT_NAME))


if __name__ == "__main__":
    main()
