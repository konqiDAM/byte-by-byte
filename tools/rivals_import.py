"""Harvest OTHER contributors' uploaded candidates for functions we can claim.

The server serves a checkpoint's source only while we hold a claim on that function,
so a sweep is: claim by address -> read function_history -> give up -> score offline.

    python exp91/rivals_import.py                      # our live claims + probe the pool
    python exp91/rivals_import.py --live-only          # only claims we already hold
    python exp91/rivals_import.py --max-functions 20 --band 1K-4K
    python exp91/rivals_import.py --addresses 0x00643540,0x00a55e90
    python exp91/rivals_import.py --rescore            # offline, 0 API requests
    python exp91/rivals_import.py --release-orphans    # crash recovery
    python exp91/rivals_import.py --dry-run

Lanes: one thread per pool slice, each with its own band, pool kind and claim batch, so
small bands are worked while the big ones are still going:

    python exp91/rivals_import.py --max-open 120 --jobs 2 --pack \\
      --lane "name=near-tiny band=<=255 pool=near sort=small batch=30 max=200" \\
      --lane "name=light-tiny band=<=255 pool=light sort=small batch=30 max=200" \\
      --lane "name=near-256 band=256-511 pool=near sort=small batch=30 max=200" \\
      --lane "name=light-512 band=512-1K pool=light sort=small batch=30 max=200"

`pool=near` is the heavily-attempted pool (most checkpoints), `pool=light` the
abandoned-on-first-try pool (fewest, cleanest attempts), `pool=any` unfiltered. Without
--lane the script runs one lane per band, near pool, smallest first. --max-open is the
hard ceiling on claims open at once across all lanes; --batch is per lane.

Config: rivals\\harvest.json holds the defaults (any option, dashes fine) plus the lane list,
so a normal run is just `python exp91\\rivals_import.py`. Command-line flags still win;
--config PATH uses another file, --no-config ignores it.

Errors: everything that goes wrong lands in ONE file, rivals\\_errors.md (a table, newest
last). Every row carrying a claim_id is a claim that may still be open, and the fix is
always `python exp91\\rivals_import.py --release-orphans`. View it with `--errors`.

Everything lands in C:\\f3decomp\\rivals\\<address>\\ :
    best.cpp   the best rival draft (copy over cand.cpp and iterate)
    best.md    their score vs ours, their note, where the file came from
    ndiff010_535b_20261112T1302Z_chk_48a14e.cpp

Safety: every claim we open is written to rivals/_claims.json first, so a crash is
cleaned up with --release-orphans. Claims we did not open (another agent's work) are
never released. Giving up never counts against the account. Nothing here submits.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

API = "https://f3decomp.com/api/v1/"
ROOT = r"C:\f3decomp"
RIVALS = os.path.join(ROOT, "rivals")
CLAIMS = os.path.join(ROOT, "claims")
SCORER = os.path.join(ROOT, "exp91", "score_pack.py")
INCOMING = os.path.join(RIVALS, "_incoming")

SEEN = os.path.join(RIVALS, "seen.json")
INDEX = os.path.join(RIVALS, "_index.json")
HELD = os.path.join(RIVALS, "_claims.json")
LOG = os.path.join(RIVALS, "_log.jsonl")
ERRORS = os.path.join(RIVALS, "_errors.md")
CONFIG = os.path.join(RIVALS, "harvest.json")
REPORT = os.path.join(RIVALS, "_report.md")
STRUCTS = os.path.join(RIVALS, "_structures.md")
STRUCTS_DB = os.path.join(RIVALS, "_structs.json")

SIZE_OF = {}

BANDS = ["<=255", "256-511", "512-1K", "1K-4K", "4K+"]

# One lane = one thread working one kind of pool. Pool kinds, and the filters each
# implies: "near" is the heavily-attempted pool (most checkpoints to take), "light" is
# the abandoned-on-first-try pool (fewest, cleanest attempts), "any" is unfiltered.
POOLS = {
    "near":  {"min_give_ups": 1, "min_near_misses": 1, "has_near_miss": True,  "max_give_ups": None},
    "light": {"min_give_ups": 1, "min_near_misses": 0, "has_near_miss": None,  "max_give_ups": 2},
    "any":   {"min_give_ups": 0, "min_near_misses": 0, "has_near_miss": None,  "max_give_ups": None},
}

# Dead ranges and paying address prefixes: measured, not guessed (see rivals\README.md).
# 0x00BA0000-0x00C40000 is the speedtree/CRT graveyard - their index spans end at the catch
# funclets, so the compiled extent can never equal the recorded size, and the CRT ones are
# detached __finally funclets reading a frame they do not own.
SKIP_RANGES = [(0x00BA0000, 0x00C40000)]
PREFIX_BOOST = ["0x0060", "0x0045", "0x0042", "0x0067", "0x006c", "0x0054"]
PREFIX_AVOID = ["0x0070", "0x005d", "0x005c"]


def parse_range(text):
    lo, _, hi = text.partition("-")
    return (int(lo, 16), int(hi, 16))


def in_skip_range(addr):
    a = int(addr, 16)
    return any(lo <= a <= hi for lo, hi in SKIP_RANGES)


def prefix_rank(addr):
    """(diluted, boost_rank): paying prefixes first, diluted ones last."""
    p = addr[:6].lower()
    if p in PREFIX_AVOID:
        return (1, 0)
    if p in PREFIX_BOOST:
        return (0, PREFIX_BOOST.index(p))
    return (0, len(PREFIX_BOOST))


class Lane:
    """A pool slice: one band, one pool kind, its own order and claim batch."""

    def __init__(self, name, band, pool, sort, batch, max_functions, addresses=None,
                 min_give_ups=None, min_near_misses=None):
        self.name = name
        self.band = band
        self.pool = pool
        self.sort = sort
        self.batch = batch
        self.max_functions = max_functions
        self.addresses = addresses or []
        spec = POOLS[pool]
        self.min_give_ups = spec["min_give_ups"] if min_give_ups is None else min_give_ups
        self.min_near_misses = (spec["min_near_misses"] if min_near_misses is None
                                else min_near_misses)

    def __repr__(self):
        return "%-12s band=%-8s pool=%-5s batch=%d max=%d" % (
            self.name, self.band, self.pool, self.batch, self.max_functions)


def parse_lane(spec, defaults):
    """`name=near-tiny band=<=255 pool=near sort=small batch=30 max=200`"""
    kv = {}
    for part in spec.split():
        if "=" not in part:
            raise SystemExit("bad --lane field %r (want key=value)" % part)
        k, v = part.split("=", 1)
        kv[k.replace("-", "_")] = v
    band = kv.get("band") or defaults["band"]
    pool = kv.get("pool") or defaults["pool"]
    if band not in BANDS:
        raise SystemExit("bad --lane band %r (one of %s)" % (band, ", ".join(BANDS)))
    if pool not in POOLS:
        raise SystemExit("bad --lane pool %r (one of %s)" % (pool, ", ".join(POOLS)))
    return Lane(kv.get("name") or "%s-%s" % (pool, band.replace("<=", "u").replace("-", "")),
                band, pool,
                kv.get("sort") or defaults["sort"],
                int(kv.get("batch") or defaults["batch"]),
                int(kv.get("max") or defaults["max_functions"]),
                min_give_ups=int(kv["give_ups"]) if "give_ups" in kv else None,
                min_near_misses=int(kv["near"]) if "near" in kv else None)


class Budget(Exception):
    pass


def now():
    return datetime.now(timezone.utc)


def stamp():
    return now().strftime("%Y%m%dT%H%MZ")


def load(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save(path, data):
    tmp = "%s.%d.tmp" % (path, threading.get_ident())   # one temp file per thread
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)
    os.replace(tmp, path)


def log(event, **kw):
    rec = {"utc": now().isoformat(timespec="seconds"), "event": event}
    rec.update(kw)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


ERROR_LOCK = threading.Lock()

ERROR_HEAD = """# Harvest errors

Everything that went wrong, one row per event, newest last. **This is the file to read when
claims need releasing** - every row that carries a `claim_id` is a claim that may still be open.

    python exp91\\rivals_import.py --release-orphans     # give back every claim this tool holds
    python exp91\\rivals_import.py --errors               # show this file, newest first

| utc | kind | address | claim_id | release? | detail |
|---|---|---|---|---|---|
"""


def error(kind, address="", claim_id="", detail=""):
    """Append one row to rivals\\_errors.md. The only place errors are written."""
    row = "| %s | %s | %s | %s | %s | %s |\n" % (
        now().strftime("%Y-%m-%d %H:%M:%S"), kind, address or "-", claim_id or "-",
        "yes" if claim_id else "-",
        (detail or "").replace("|", "/").replace("\n", " ")[:300])
    with ERROR_LOCK:
        new = not os.path.isfile(ERRORS)
        with open(ERRORS, "a", encoding="utf-8") as f:
            if new:
                f.write(ERROR_HEAD)
            f.write(row)


def key():
    return open(os.path.join(os.environ["USERPROFILE"], ".f3decomp_key")).read().strip()


class Api:
    def __init__(self, budget):
        self.budget = budget
        self.used = 0
        self.lock = threading.Lock()

    def post(self, path, body=None):
        with self.lock:
            if self.used >= self.budget:
                raise Budget()
            self.used += 1
        for attempt in range(3):
            req = urllib.request.Request(
                API + path, data=json.dumps(body or {}).encode(),
                headers={"Authorization": "Bearer " + key(), "User-Agent": "Mozilla/5.0",
                         "Content-Type": "application/json"})
            try:
                raw = urllib.request.urlopen(req, timeout=120).read().decode()
                return json.loads(raw or "{}")
            except urllib.error.HTTPError as e:
                txt = e.read().decode()[:300]
                if e.code == 429 and attempt < 2:
                    time.sleep(10 * (attempt + 1))
                    continue
                return {"__err": e.code, "body": txt}
            except Exception as e:
                if attempt < 2:
                    time.sleep(3)
                    continue
                return {"__err": "exc", "body": str(e)[:200]}
        return {"__err": "retries"}

    def get_raw(self, url):
        if self.used >= self.budget:
            raise Budget()
        self.used += 1
        if not url.startswith("http"):
            url = "https://f3decomp.com" + ("" if url.startswith("/") else "/") + url
        req = urllib.request.Request(url, headers={"Authorization": "Bearer " + key(),
                                                   "User-Agent": "Mozilla/5.0"})
        try:
            return urllib.request.urlopen(req, timeout=300).read()
        except Exception as e:
            return {"__err": str(e)[:200]}


# ---------------------------------------------------------------- packs on disk

PACK_DIRS = {}  # claim_id -> pack directory (the folder name IS the claim id)


def pack_map():
    """address -> pack directory, plus PACK_DIRS and SIZE_OF from each pack.json.

    A claim's own folder is authoritative: several packs can exist for one address
    (a stale one from an older claim), so the claim id wins over the address map.
    """
    out = {}
    if not os.path.isdir(CLAIMS):
        return out
    for d in sorted(os.listdir(CLAIMS)):
        p = os.path.join(CLAIMS, d, "pack.json")
        if not os.path.isfile(p):
            continue
        m = load(p, {})
        if not m.get("address"):
            continue
        a = m["address"].lower()
        out.setdefault(a, os.path.join(CLAIMS, d))
        PACK_DIRS[d] = os.path.join(CLAIMS, d)
        if m.get("size"):
            SIZE_OF.setdefault(a, m["size"])
    return out


# ---------------------------------------------------------------- scoring

SCORE_RE = re.compile(r"status=(\S+)\s+ndiff=(\d+)\s+extent=(\d+)\s+errs=(\d+)")


def score(pack, path):
    try:
        p = subprocess.run([sys.executable, SCORER, pack, path],
                           capture_output=True, text=True, timeout=3600)
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "ndiff": None, "extent": None, "errs": None}
    m = SCORE_RE.search(p.stdout or "")
    if not m:
        return {"status": "score_failed", "ndiff": None, "extent": None, "errs": None}
    return {"status": m.group(1), "ndiff": int(m.group(2)),
            "extent": int(m.group(3)), "errs": int(m.group(4))}


def rank(rec):
    if rec.get("ndiff") is None:
        return (1 << 30, 1 << 30)
    return (rec["ndiff"], rec.get("errs") or 0)


# ---------------------------------------------------------------- structures

DECL_RE = re.compile(r"(?m)^[ \t]*(struct|class|union|enum)\s+([A-Za-z_]\w*)")
EXTERN_RE = re.compile(r"(?m)^[ \t]*extern\b[^;{}\n]*;")
STRUCTS_LOCK = threading.Lock()


def extract_decls(text):
    found = []
    for m in DECL_RE.finditer(text):
        open_at = text.find("{", m.end())
        semi = text.find(";", m.end())
        if open_at < 0 or (0 <= semi < open_at):
            continue
        depth, i = 0, open_at
        while i < len(text):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        body = text[m.start():i + 1].strip()
        if len(body) > 6000:
            body = body[:6000] + "\n/* truncated */"
        found.append((m.group(1), m.group(2), body))
    for m in EXTERN_RE.finditer(text):
        line = m.group(0).strip()
        found.append(("extern", line, line))
    return found


def absorb_structs(addr, chk, text):
    # lanes harvest in parallel: load+save of one shared file must not interleave, or
    # os.replace hits the reader's open handle (WinError 5)
    with STRUCTS_LOCK:
        db = load(STRUCTS_DB, {})
        new = 0
        for kind, name, body in extract_decls(text):
            k = body if kind == "extern" else "%s %s" % (kind, name)
            if k in db:
                continue
            db[k] = {"kind": kind, "name": name, "body": body, "address": addr,
                     "checkpoint": chk, "utc": now().isoformat(timespec="seconds")}
            new += 1
        if new:
            save(STRUCTS_DB, db)
        return new


def write_structures():
    db = load(STRUCTS_DB, {})
    lines = ["# Declarations harvested from other contributors", "",
             "%d unique declarations, newest first." % len(db), ""]
    for _, v in sorted(db.items(), key=lambda kv: kv[1]["utc"], reverse=True):
        title = v["name"] if v["kind"] != "extern" else "extern"
        lines += ["## %s  (%s, %s)" % (title, v["address"], v["utc"]),
                  "```cpp", v["body"], "```", ""]
    with open(STRUCTS, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# ---------------------------------------------------------------- per address

def addr_dir(addr):
    d = os.path.join(RIVALS, addr)
    os.makedirs(d, exist_ok=True)
    return d


def write_best(addr, info):
    cps = [c for c in info.get("checkpoints", []) if c.get("file")]
    ours = info.get("ours") or {}
    if not cps:
        return
    best = sorted(cps, key=rank)[0]
    src = os.path.join(addr_dir(addr), best["file"])
    if not os.path.isfile(src):
        return
    shutil.copyfile(src, os.path.join(addr_dir(addr), "best.cpp"))
    their, our = best.get("ndiff"), ours.get("ndiff")
    gain = (our - their) if (our is not None and their is not None) else None
    info["best"] = {"file": best["file"], "ndiff": their, "extent": best.get("extent"),
                    "errs": best.get("errs"), "checkpoint": best["checkpoint_id"]}
    info["gain"] = gain
    artefact = ""
    if their == 0 and ((best.get("errs") or 0) > 0
                       or best.get("extent") != info.get("size")):
        artefact = ("**ndiff 0 but extent %s vs size %s - a span artefact, NOT a match**"
                    % (best.get("extent"), info.get("size")))
        info["artefact"] = True
    md = ["# %s  (%s bytes)" % (addr, info.get("size") or SIZE_OF.get(addr) or "?"), "",
          "rival best: %.0f ndiff, extent %s, errs %s" % (their if their is not None else -1,
                                                          best.get("extent"), best.get("errs")),
          "  from checkpoint %s, %s" % (best["checkpoint_id"], best.get("when")),
          "ours best:  %s ndiff, extent %s, errs %s" % (our, ours.get("extent"), ours.get("errs")),
          "improvement: %s" % ("%d instructions" % gain if gain is not None else "unknown"),
          "", artefact, "their note: %s" % (best.get("note") or "-"), "",
          "use:", "```", r"copy C:\f3decomp\rivals\%s\best.cpp <packdir>\cand.cpp" % addr,
          "```",
          "Their draft is a lead, not a match - verify every byte with f3check before submitting."]
    with open(os.path.join(addr_dir(addr), "best.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")


def absorb_best_attempts(addr, claim_id, packet):
    """The packet carries the site's best attempts: other contributors' closest code.

    A 'lean' packet has none - ask for 'resume'. This code is not in the checkpoints (a near
    miss the server never serves again), so it is worth a file of its own.
    """
    info_path = os.path.join(addr_dir(addr), "index.json")
    info = load(info_path, {"address": addr, "checkpoints": []})
    known = {c.get("sha256") for c in info.get("checkpoints", [])}
    n = 0
    for a in packet.get("best_attempts") or []:
        code = a.get("code") or ""
        if not code or a.get("from") == "you":
            continue
        sha = hashlib.sha256(code.encode("utf-8", "surrogateescape")).hexdigest()
        if sha in known:
            continue
        tmp = os.path.join(INCOMING, "ba_%s_%s.cpp" % (sha[:16], claim_id))
        with open(tmp, "w", encoding="utf-8", newline="") as f:
            f.write(code)
        info["checkpoints"].append({"checkpoint_id": "best_attempt_" + sha[:12],
                                    "when": a.get("when"), "kind": "best_attempt",
                                    "note": (a.get("reason") or "")[:600],
                                    "sha256": sha, "tmp": tmp, "site_score": a.get("score"),
                                    "ndiff": None, "extent": None, "errs": None})
        known.add(sha)
        n += 1
    if n:
        save(info_path, info)
    return n


def fetch_pack(api, claim_id, addr):
    """Download the pack while we hold the claim, so the rival code can be scored offline.

    The pack is the whole work folder (pack.json, headers, unit_*.cpp): with it a rival
    draft is a drop-in candidate and our scorer runs with 0 API requests.
    """
    d = os.path.join(CLAIMS, claim_id)
    if os.path.isfile(os.path.join(d, "pack.json")):
        PACK_DIRS[claim_id] = d
        return d, None
    p = api.post("packet", {"claim_id": claim_id, "context_mode": "resume"})
    if p.get("__err") or not p.get("pack_url"):
        return None, p
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "packet.json"), "w", encoding="utf-8") as f:
        json.dump(p, f, indent=1)
    raw = api.get_raw(p["pack_url"])
    if isinstance(raw, dict):
        return None
    tar_path = os.path.join(d, "pack.tar.gz")
    with open(tar_path, "wb") as f:
        f.write(raw)
    try:
        import tarfile
        with tarfile.open(tar_path) as tf:
            tf.extractall(d)
    except Exception as e:
        print("  %s pack extract failed: %s" % (addr, str(e)[:80]))
        error("pack_extract", addr, claim_id, str(e)[:200])
        return None, p
    if os.path.isfile(os.path.join(d, "pack.json")):
        PACK_DIRS[claim_id] = d
        SIZE_OF.setdefault(addr, load(os.path.join(d, "pack.json"), {}).get("size"))
        log("pack", address=addr, claim_id=claim_id, bytes=len(raw))
        return d, p
    return None, p


def our_score(info, packs, addr):
    pack = info.get("pack") or packs.get(addr)
    info["pack"] = pack
    cand = os.path.join(pack, "cand.cpp") if pack else None
    if not cand or not os.path.isfile(cand):
        info["ours"] = {"file": cand, "ndiff": None, "extent": None, "errs": None,
                        "note": "no pack/cand.cpp on disk"}
        return
    st = os.stat(cand)
    prev = info.get("ours") or {}
    if prev.get("file") == cand and prev.get("mtime") == st.st_mtime:
        return
    r = score(pack, cand)
    info["ours"] = {"file": cand, "mtime": st.st_mtime, "ndiff": r["ndiff"],
                    "extent": r["extent"], "errs": r["errs"], "status": r["status"]}
    log("score_ours", address=addr, ndiff=r["ndiff"], extent=r["extent"], errs=r["errs"])


def fetch_rivals(api, addr, claim_id, seen, lane=""):
    """Read the history of a function we hold; download unseen rival checkpoints."""
    info_path = os.path.join(addr_dir(addr), "index.json")
    info = load(info_path, {"address": addr, "checkpoints": []})
    info["address"] = addr
    if lane:
        info["lane"] = lane
    info["size"] = info.get("size") or SIZE_OF.get(addr)
    info["pack"] = PACK_DIRS.get(claim_id) or info.get("pack")
    h = api.post("function_history", {"address": addr, "claim_id": claim_id,
                                      "view": "list", "limit": 50})
    if h.get("__err"):
        body = h.get("body") or ""
        # a claim released mid-run answers 409; that is a skip, not an error
        if h.get("__err") == 409:
            info["last_result"] = "claim already gone: " + body[:120]
            print("  %s skip (%s)" % (addr, body[:60]))
        else:
            info.setdefault("errors", []).append("history %s: %s" % (h["__err"], body))
            error("history_failed", addr, claim_id, "HTTP %s %s" % (h["__err"], body[:200]))
        info["last_scan_utc"] = now().isoformat(timespec="seconds")
        save(info_path, info)
        return info, 0, 0
    cps = h.get("checkpoints") or []
    info["checkpoints_total"] = len(cps)
    known = {c["checkpoint_id"] for c in info.get("checkpoints", [])}
    by_sha = {c["sha256"]: c for c in info.get("checkpoints", []) if c.get("sha256")}
    new = dup = 0
    for c in cps:
        cid, who = c.get("checkpoint_id"), c.get("from")
        if who != "another contributor" or not c.get("has_source") or not cid:
            continue
        if cid in seen or cid in known:
            dup += 1
            continue
        s = api.post("function_history", {"address": addr, "claim_id": claim_id,
                                          "view": "source", "checkpoint_id": cid})
        src = s.get("source")
        if not src:
            info.setdefault("errors", []).append(
                "source %s: %s" % (cid, s.get("__err") or s.get("body") or "empty"))
            error("source_missing", addr, claim_id,
                  "%s: %s" % (cid, (s.get("__err") or s.get("body") or "empty")))
            continue
        sha = hashlib.sha256(src.encode("utf-8", "surrogateescape")).hexdigest()
        if sha in by_sha:
            by_sha[sha].setdefault("aliases", []).append(cid)
            seen[cid] = {"address": addr, "sha256": sha, "file": by_sha[sha].get("file"),
                         "first_seen_utc": now().isoformat(timespec="seconds"),
                         "alias_of": by_sha[sha]["checkpoint_id"]}
            dup += 1
            continue
        tmp = os.path.join(INCOMING, cid + ".cpp")
        with open(tmp, "w", encoding="utf-8", newline="") as f:
            f.write(src)
        rec = {"checkpoint_id": cid, "when": c.get("when"), "note": c.get("note") or "",
               "sha256": sha, "tmp": tmp, "ndiff": None, "extent": None, "errs": None}
        info["checkpoints"].append(rec)
        by_sha[sha] = rec
        absorb_structs(addr, cid, src)
        new += 1
    info["last_scan_utc"] = now().isoformat(timespec="seconds")
    save(info_path, info)
    log("fetch", address=addr, lane=lane, new=new, seen_already=dup, checkpoints=len(cps))
    return info, new, dup


def finalize(addr, info, packs, jobs, seen, rescore=False):
    d = addr_dir(addr)
    pack = info.get("pack") or packs.get(addr)
    if rescore:
        todo = [c for c in info.get("checkpoints", []) if c.get("file")]
        for c in todo:
            c["job"] = os.path.join(d, c["file"])
    else:
        todo, seen_tmp = [], set()
        for c in info.get("checkpoints", []):
            if c.get("tmp") and os.path.isfile(c["tmp"]) and c["tmp"] not in seen_tmp:
                seen_tmp.add(c["tmp"])
                todo.append(c)
        for c in todo:
            c["job"] = c["tmp"]
    if pack and todo:
        with ThreadPoolExecutor(max_workers=max(1, jobs)) as ex:
            results = list(ex.map(lambda c: score(pack, c["job"]), todo))
        for c, r in zip(todo, results):
            c.update({k: r[k] for k in ("ndiff", "extent", "errs", "status")})
    if not rescore:
        for c in todo:
            nd = c.get("ndiff")
            name = ("ndiff%04d_%sb_%s_chk_%s.cpp"
                    % (nd, c.get("extent") or 0, stamp(), c["checkpoint_id"][-8:])
                    if nd is not None else
                    "unscored_%s_chk_%s.cpp" % (stamp(), c["checkpoint_id"][-8:]))
            try:
                os.replace(c["tmp"], os.path.join(d, name))
            except OSError as e:
                print("  %s rename skipped (%s): %s" % (addr, c.get("checkpoint_id"), str(e)[:60]))
                continue
            c["file"] = name
            seen.setdefault(c["checkpoint_id"], {}).update({"file": name, "ndiff": c.get("ndiff")})
    for c in todo:
        c.pop("job", None)
        c.pop("tmp", None)
    for c in info.get("checkpoints", []):
        if not (c.get("file") or "").startswith("unscored_") or c.get("ndiff") is None:
            continue
        name = "ndiff%04d_%sb_%s_chk_%s.cpp" % (c["ndiff"], c.get("extent") or 0,
                                                stamp(), c["checkpoint_id"][-8:])
        os.replace(os.path.join(d, c["file"]), os.path.join(d, name))
        c["file"] = name
        seen.setdefault(c["checkpoint_id"], {}).update({"file": name, "ndiff": c["ndiff"]})
    our_score(info, packs, addr)
    write_best(addr, info)
    save(os.path.join(d, "index.json"), info)
    return info


def prune_drafts(infos):
    """Delete the drafts that are not usable (compile error, or wrong extent).

    Measured: 200 usable out of 1011 scored. The other ~800 are why the corpus is 8 MB, and
    no C++ spelling of a wrong extent ever becomes a match. best.cpp stays for every address,
    so one file per address is still there to look at.
    """
    files = freed = 0
    for addr, info in infos.items():
        best = info.get("best") or {}
        size = info.get("size") or 0
        usable = (best.get("ndiff") is not None and (best.get("errs") or 0) == 0
                  and best.get("extent") == size)
        if usable:
            continue
        d = os.path.join(RIVALS, addr)
        kept = False
        for c in info.get("checkpoints") or []:
            f = c.get("file")
            if not f:
                continue
            p = os.path.join(d, f)
            if os.path.isfile(p):
                files += 1
                freed += os.path.getsize(p)
                os.remove(p)
            c["pruned"] = True
            c["file"] = None
            kept = True
        if kept:
            if os.path.isfile(os.path.join(d, "best.cpp")):
                info["best"]["file"] = "best.cpp"
            save(os.path.join(d, "index.json"), info)
    print("pruned %d files, %.1f MB" % (files, freed / 1e6))


def scan_infos():
    out = {}
    if not os.path.isdir(RIVALS):
        return out
    for d in sorted(os.listdir(RIVALS)):
        p = os.path.join(RIVALS, d, "index.json")
        if os.path.isfile(p):
            out[d] = load(p, {})
    return out


# ---------------------------------------------------------------- pool

def lane_targets(api, lane, args, held, idx):
    """This lane's own slice of the pool: one band, one pool kind, one order."""
    spec = POOLS[lane.pool]
    out, seen_addr = [], set(held)
    skipped = 0
    r = api.post("list_functions", {"band": lane.band, "order": "give_ups",
                                    "max_give_ups": spec["max_give_ups"] or 9999,
                                    "has_near_miss": spec["has_near_miss"],
                                    "exclude_reported": args.exclude_reported, "limit": 500})
    if r.get("__err"):
        print("  [%s] list_functions %s: %s" % (lane.name, lane.band, r.get("body")))
        error("list_functions", "", "", "%s: HTTP %s %s"
              % (lane.band, r.get("__err"), (r.get("body") or "")[:200]))
        return out
    for f in r.get("functions") or []:
        a = f["address"].lower()
        if a in seen_addr:
            continue
        if in_skip_range(a):
            skipped += 1
            continue
        if (f.get("size") or 0) < args.min_size:
            continue
        if (f.get("give_ups") or 0) < lane.min_give_ups:
            continue
        if spec["max_give_ups"] is not None and (f.get("give_ups") or 0) > spec["max_give_ups"]:
            continue
        if (f.get("near_misses") or 0) < lane.min_near_misses:
            continue
        if (f.get("flagged") or {}).get("state") == "reproduced":
            continue
        last = (idx.get(a) or {}).get("last_scan_utc")
        if last and args.max_age > 0:
            if (now() - datetime.fromisoformat(last)).total_seconds() / 3600.0 < args.max_age:
                continue
        SIZE_OF[a] = f.get("size")
        seen_addr.add(a)
        out.append(a)
    if lane.sort == "size":
        out.sort(key=lambda a: -(SIZE_OF.get(a) or 0))
    elif lane.sort == "small":
        out.sort(key=lambda a: (SIZE_OF.get(a) or 0))
    elif lane.sort == "paid":
        # measured: the paying prefixes first, the dilute ones last, biggest first inside
        out.sort(key=lambda a: (prefix_rank(a), -(SIZE_OF.get(a) or 0)))
    print("  [%s] %s %s pool: %d candidates (%d skipped as dead range)"
          % (lane.name, lane.band, lane.pool, len(out), skipped))
    return out


# ---------------------------------------------------------------- claims

def held_claims():
    return load(HELD, {"claims": []})


CLAIMS_LOCK = threading.Lock()


def remember(claim_id, addr):
    with CLAIMS_LOCK:
        h = held_claims()
        if not any(c["claim_id"] == claim_id for c in h["claims"]):
            h["claims"].append({"claim_id": claim_id, "address": addr,
                                "claimed_utc": now().isoformat(timespec="seconds")})
            save(HELD, h)


def forget(claim_id):
    with CLAIMS_LOCK:
        h = held_claims()
        h["claims"] = [c for c in h["claims"] if c["claim_id"] != claim_id]
        save(HELD, h)


def release(api, claim_id, addr):
    # the server occasionally answers giveup with a transient {"error":"internal error"};
    # a claim left open blocks that function for everyone until it lapses
    r = {}
    for attempt in range(3):
        r = api.post("giveup", {"claim_id": claim_id, "category": "other",
                                "tried": "recon only: imported rival checkpoints, no edits.",
                                "still_differs": "not worked in this claim.",
                                "suspected_cause": "n/a - recon claim, released immediately.",
                                "model": "rivals_import"})
        if "__err" not in r or r.get("__err") == 409:
            break
        time.sleep(2 * (attempt + 1))
    ok = "__err" not in r
    if ok or r.get("__err") == 409:
        forget(claim_id)  # 409: already lapsed or released elsewhere
    else:
        error("giveup_failed", addr, claim_id,
              "HTTP %s %s - the claim is still open, run --release-orphans"
              % (r.get("__err"), (r.get("body") or "")[:200]))
    print("  %s release %s %s" % (addr, claim_id, "ok" if ok else "FAILED, kept for --release-orphans"))
    log("release", address=addr, claim_id=claim_id, ok=ok, body=r.get("body"))


def release_orphans(api):
    st = api.post("status", {})
    open_ids = {c["claim_id"] for c in st.get("open_claims") or []}
    n = 0
    for c in list(held_claims()["claims"]):
        if c["claim_id"] not in open_ids:
            forget(c["claim_id"])
            continue
        print("  orphan %s %s" % (c["address"], c["claim_id"]))
        release(api, c["claim_id"], c["address"])
        n += 1
    print("orphans released: %d" % n)


# ---------------------------------------------------------------- report

def write_report(infos):
    """Near misses first, then what is usable right now, then ours-vs-theirs, then the
    per-lane yield (which pool pays) and a grep-friendly one line per address."""
    leads = []
    for a, info in infos.items():
        best, ours = info.get("best") or {}, info.get("ours") or {}
        cands = []
        if best.get("ndiff") is not None:
            cands.append((best["ndiff"], "rival", best))
        if ours.get("ndiff") is not None:
            cands.append((ours["ndiff"], "ours", ours))
        if not cands:
            continue
        n, who, rec = min(cands, key=lambda t: t[0])
        size = info.get("size") or SIZE_OF.get(a)
        ext, errs = rec.get("extent"), rec.get("errs")
        leads.append({"ndiff": rec.get("ndiff"), "who": who, "addr": a, "size": size,
                      "extent": ext, "errs": errs, "file": rec.get("file"),
                      "lane": info.get("lane") or "-",
                      # usable = it compiles clean AND the size is the original's size
                      "usable": bool(size and ext and ext == size and (errs or 0) == 0)})
    leads.sort(key=lambda r: (r["ndiff"], not r["usable"], r["size"] or 0))
    rows = []
    for a, info in infos.items():
        best, ours = info.get("best") or {}, info.get("ours") or {}
        gain = info.get("gain")
        rows.append((gain if gain is not None else -10 ** 6, a,
                     info.get("size") or SIZE_OF.get(a),
                     ours.get("ndiff"), best.get("ndiff"), best.get("extent"),
                     best.get("errs"), best.get("file")))
    rows.sort(reverse=True)
    usable = [r for r in leads if r["usable"]]
    lines = ["# Rival code harvest - %s" % now().strftime("%Y-%m-%d %H:%M UTC"), "",
             "%d addresses with imported rival code, %d with a scored candidate, "
             "**%d usable right now** (0 compile errors and the original's exact size)."
             % (len(infos), len(leads), len(usable)),
             "", "## Usable now - start here", "",
             "Twins (the original FNV source for these functions) are in `rivals\\_twins.md` -",
             "57 usable drafts already carry one, and a twin is faster to port than a draft.",
             "",
             "| ndiff | who | function | size | lane | file |", "|---|---|---|---|---|---|"]
    for r in usable[:40]:
        lines.append("| **%s** | %s | `%s` | %s | %s | %s |"
                     % (r["ndiff"], r["who"], r["addr"], r["size"], r["lane"],
                        (r["file"] or "-")[:52]))
    lines += ["", "## The near misses (closest to a match - ours or theirs)", "",
              "ndiff = instructions that differ, extent = the compiled size, errs = compile errors,",
              "`usable` means it compiles clean and its size equals the original's.",
              "",
              "| ndiff | who | function | size | extent | errs | usable | lane | file |",
              "|---|---|---|---|---|---|---|---|---|"]
    for r in leads[:60]:
        lines.append("| %s%s%s | %s | `%s` | %s | %s | %s | %s | %s | %s |"
                     % ("**" if r["usable"] else "", r["ndiff"], "**" if r["usable"] else "",
                        r["who"], r["addr"],
                        r["size"] or "-", "-" if r["extent"] is None else r["extent"],
                        "-" if r["errs"] is None else r["errs"],
                        "yes" if r["usable"] else "", r["lane"], r["file"] or "-"))
    lines += ["", "## Yield per lane (which pool is worth working)", "",
              "| lane | addresses | scored | usable | best ndiff |", "|---|---|---|---|---|"]
    tally = {}
    for a, info in infos.items():
        t = tally.setdefault(info.get("lane") or "-", {"addr": 0, "scored": 0, "usable": 0,
                                                       "best": None})
        t["addr"] += 1
    for r in leads:
        t = tally.setdefault(r["lane"], {"addr": 0, "scored": 0, "usable": 0, "best": None})
        t["scored"] += 1
        t["usable"] += 1 if r["usable"] else 0
        if t["best"] is None or r["ndiff"] < t["best"]:
            t["best"] = r["ndiff"]
    for name in sorted(tally):
        t = tally[name]
        lines.append("| %s | %d | %d | %d | %s |"
                     % (name, t["addr"], t["scored"], t["usable"],
                        "-" if t["best"] is None else t["best"]))
    lines += ["", "## Ours vs theirs (the gain we would get)", "",
              "| function | size | ours | rival | gain | rival extent | errs | file |",
              "|---|---|---|---|---|---|---|---|"]
    for gain, a, size, our, their, ext, errs, fn in rows[:80]:
        g = "-" if gain < -10 ** 5 else gain
        lines.append("| `%s` | %s | %s | %s | %s | %s | %s | %s |"
                     % (a, size or "-", "-" if our is None else our,
                        "-" if their is None else their, g,
                        "-" if ext is None else ext, "-" if errs is None else errs, fn or "-"))
    lines += ["", "## Grep index (address ndiff= size= extent= errs= usable= lane=)", ""]
    for r in leads:
        lines.append("%s ndiff=%s size=%s extent=%s errs=%s usable=%s lane=%s"
                     % (r["addr"], r["ndiff"], r["size"] or "-",
                        "-" if r["extent"] is None else r["extent"],
                        "-" if r["errs"] is None else r["errs"],
                        "yes" if r["usable"] else "no", r["lane"]))
    lines += ["", "Use a candidate:", "```",
              r"copy C:\f3decomp\rivals\<address>\best.cpp <packdir>\cand.cpp", "```", "",
              "A rival draft is a lead, never a match: check every byte with f3check."]
    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------- main

def self_test():
    """Assert the lane bits that would burn the account if wrong. No API, no claims."""
    d = {"sort": "small", "band": "<=255", "pool": "near", "batch": 30, "max_functions": 200}
    a = parse_lane("name=x band=<=255 pool=near sort=size batch=7 max=9", d)
    assert (a.name, a.band, a.pool, a.sort, a.batch, a.max_functions) == \
        ("x", "<=255", "near", "size", 7, 9), a
    assert a.min_give_ups == 1 and a.min_near_misses == 1     # near = the attempted pool
    b = parse_lane("name=y pool=light", d)
    assert (b.band, b.batch, b.max_functions) == ("<=255", 30, 200), b
    assert b.min_near_misses == 0 and POOLS["light"]["max_give_ups"] == 2
    c = parse_lane("name=z pool=near give_ups=3 near=0", d)
    assert (c.min_give_ups, c.min_near_misses) == (3, 0), c
    for bad in ("name=q band=nope", "name=q pool=nope", "badfield"):
        try:
            parse_lane(bad, d)
        except SystemExit:
            pass
        else:
            raise AssertionError("parse_lane accepted %r" % bad)
    # the ceiling: --max-open must admit exactly that many claims, never one more
    slots = threading.Semaphore(100)
    held = []
    for _ in range(100):
        assert slots.acquire(blocking=False), "slot %d refused below the ceiling" % len(held)
        held.append(1)
    assert not slots.acquire(blocking=False), "the ceiling admitted claim 101"
    for _ in held:
        slots.release()
    # and the batch acquire/release pattern of run_lane must not deadlock or leak
    lock = threading.Lock()
    state = {"now": 0, "peak": 0}

    def lane_body():
        for _ in range(4):                              # 4 batches, the way run_lane claims
            got = []
            for _ in range(20):                         # 4 lanes x 20 stays under the ceiling
                assert slots.acquire(timeout=10), "lane blocked: a slot was leaked"
                with lock:
                    state["now"] += 1
                    state["peak"] = max(state["peak"], state["now"])
                got.append(1)
                time.sleep(0.001)                       # pretend each claim is a round trip
            for _ in got:                               # then release the whole batch
                with lock:
                    state["now"] -= 1
                slots.release()

    ts = [threading.Thread(target=lane_body) for _ in range(4)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    assert state["peak"] <= 100, "over the claim ceiling: %d" % state["peak"]
    assert state["now"] == 0, "slots leaked: %d" % state["now"]
    print("self-test OK: lane parsing, pool defaults, 100-claim ceiling (peak %d)"
          % state["peak"])


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)   # a killed run must not lose its log tail
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument("--config", default="")
    pre.add_argument("--no-config", action="store_true")
    pre_args, _ = pre.parse_known_args()
    cfg_path = "" if pre_args.no_config else (pre_args.config or CONFIG)
    cfg = load(cfg_path, {})
    if cfg and not isinstance(cfg, dict):
        raise SystemExit("config %s must be a JSON object" % cfg_path)
    lanes_cfg = list(cfg.get("lanes") or [])
    ap.add_argument("--config", default="")
    ap.add_argument("--no-config", action="store_true")
    ap.add_argument("--band", action="append")
    ap.add_argument("--addresses", default="")
    ap.add_argument("--min-size", type=int, default=0,
                    help="skip functions smaller than this (0 = all: the report marks which "
                         "drafts are actually usable, so tiny stubs cost requests but no clutter)")
    ap.add_argument("--min-give-ups", type=int, default=2)
    ap.add_argument("--min-near-misses", type=int, default=2)
    ap.add_argument("--max-functions", type=int, default=40)
    ap.add_argument("--batch", type=int, default=60,
                    help="claims an explicit --lane opens together (default lanes size their "
                         "own batch from --max-open); --max-open is the hard ceiling")
    ap.add_argument("--jobs", type=int, default=8,
                    help="harvest threads in TOTAL, split across lanes. The API caps a run at "
                         "25k requests/hour (~50 functions/minute at ~9 requests each), so more "
                         "than ~12 only burns rate limit - the cores are idle because fetching "
                         "is waiting, not computing")
    ap.add_argument("--score-jobs", type=int, default=max(2, min(24, (os.cpu_count() or 8) - 2)),
                    help="candidates compiled in parallel in the scoring pass (default: cores-2, "
                         "capped at 24 - this is the CPU-heavy part of a run on a many-core box)")
    ap.add_argument("--budget", type=int, default=4000)
    ap.add_argument("--max-age", type=float, default=6.0)
    ap.add_argument("--max-minutes", type=float, default=40.0)
    ap.add_argument("--live-only", action="store_true")
    ap.add_argument("--keep", action="store_true")
    ap.add_argument("--rescore", action="store_true")
    ap.add_argument("--release-orphans", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--exclude-reported", action="store_true",
                    help="skip functions with an open problem report (off by default: most of "
                         "the pool carries one, and their rival code is still worth taking)")
    ap.add_argument("--sort", choices=["paid", "size", "small", "attempts"], default="paid",
                    help="order inside a lane: paid (measured-paying address prefixes first, "
                         "biggest first), size, small, or attempts. attempts is measured "
                         "BACKWARDS - near_misses 0-2 yields 14%% close drafts, 21-50 yields 4%%")
    ap.add_argument("--skip-range", action="append",
                    help="exclude an address range, e.g. '0x00BA0000-0x00C40000' (the "
                         "speedtree/CRT graveyard: their index spans end at the catch funclets, "
                         "so the extent can never match)")
    ap.add_argument("--prefix-boost", action="append",
                    help="address prefix to prefer, e.g. 0x0060 (repeatable, earlier = stronger)")
    ap.add_argument("--prefix-avoid", action="append",
                    help="address prefix to send last, e.g. 0x0070 (repeatable)")
    ap.add_argument("--lane-mode", choices=["sequential", "parallel"], default="sequential",
                    help="sequential works the lanes in the order given, so a time or request "
                         "cap hits the worst lane last (this is the point of the order)")
    ap.add_argument("--prune", action="store_true",
                    help="after scoring, delete the drafts that do not compile clean at the "
                         "exact size (keeps best.cpp for every address, cuts the corpus size)")
    ap.add_argument("--pack", action="store_true",
                    help="download the pack for every probe claim (2 extra requests, scoring works)")
    ap.add_argument("--lane", action="append",
                    help="one worker lane: 'name=near-tiny band=<=255 pool=near sort=small "
                         "batch=30 max=200'. Repeat it to run lanes in parallel. Without it, "
                         "one lane per band, pool=near, smallest first.")
    ap.add_argument("--max-open", type=int, default=120,
                    help="claims open at once across ALL lanes (swarm allows 150; keep headroom "
                         "for the other agent)")
    ap.add_argument("--self-test", action="store_true",
                    help="check the lane parsing and the claim ceiling offline, then exit")
    ap.add_argument("--errors", action="store_true",
                    help="print rivals\\_errors.md, newest first (every claim that may still be "
                         "open is a row in it), then exit")
    args = ap.parse_args()
    args.band = args.band or BANDS

    # config supplies DEFAULTS only - anything typed on the command line still wins
    for k, v in cfg.items():
        if k != "lanes":
            ap.set_defaults(**{k.replace("-", "_"): v})
    args = ap.parse_args()
    args.band = args.band or BANDS
    if lanes_cfg and not args.lane:
        args.lane = lanes_cfg
    # the measured policy lives in module globals; config/lane sort=paid reads them
    global SKIP_RANGES, PREFIX_BOOST, PREFIX_AVOID
    if args.skip_range:
        SKIP_RANGES = [parse_range(r) for r in args.skip_range]
    if args.prefix_boost:
        PREFIX_BOOST = [p.lower() for p in args.prefix_boost]
    if args.prefix_avoid:
        PREFIX_AVOID = [p.lower() for p in args.prefix_avoid]
    if cfg:
        print("config %s (%d lanes)" % (cfg_path, len(args.lane or [])))
    print("skip ranges: %s | boost %s | avoid %s"
          % (", ".join("%08x-%08x" % r for r in SKIP_RANGES) or "none",
             " ".join(PREFIX_BOOST) or "none", " ".join(PREFIX_AVOID) or "none"))

    if args.self_test:
        self_test()
        return

    if args.errors:
        if not os.path.isfile(ERRORS):
            print("no errors logged (%s does not exist)" % ERRORS)
            return
        lines = open(ERRORS, encoding="utf-8").read().splitlines()
        rows = [l for l in lines if l.startswith("| 20")]
        print("\n".join([l for l in lines if not l.startswith("| 20")]
                        + list(reversed(rows[-40:]))))
        print("\n%d rows in total. Any row with a claim_id: "
              "python exp91\\rivals_import.py --release-orphans" % len(rows))
        return

    os.makedirs(RIVALS, exist_ok=True)
    os.makedirs(INCOMING, exist_ok=True)
    seen = load(SEEN, {})
    # the per-address index.json files are always current; _index.json is only written at the
    # end of a run, so after a crash it is stale and --max-age would let us re-probe
    idx = scan_infos()
    packs = pack_map()
    api = Api(args.budget)
    t0 = time.time()

    if args.release_orphans:
        release_orphans(api)
        return

    if args.rescore:
        infos = scan_infos()
        with ThreadPoolExecutor(max_workers=max(1, args.score_jobs)) as ex:
            list(ex.map(lambda kv: finalize(kv[0], kv[1], packs, 1, seen, rescore=True), infos.items()))
        save(SEEN, seen)
        save(INDEX, scan_infos())
        write_report(scan_infos())
        write_structures()
        print("rescored %d addresses, 0 API requests, %d seen checkpoints"
              % (len(infos), len(seen)))
        return

    st = api.post("status", {})
    live = [(c["address"].lower(), c["claim_id"]) for c in st.get("open_claims") or []]
    live_pairs = set(live)
    held = {a for a, _ in live}
    print("tier %s | claims held %d | budget %d requests"
          % (st.get("tier"), len(live), args.budget))

    imported = dup = ba_added = 0

    def harvest(addr, claim_id, ours_to_keep, lane=""):
        """One function: take its pack, its rival checkpoints and its best attempts.

        Returns (new_files, known_files, best_attempt_files); the claim is released
        by the caller, so a batch can be harvested in parallel and released together.
        """
        packet = None
        if not ours_to_keep and args.pack:
            _, packet = fetch_pack(api, claim_id, addr)
        if not packet or packet.get("__err"):
            packet = api.post("packet", {"claim_id": claim_id, "context_mode": "resume"})
        ba = 0
        if packet and not packet.get("__err"):
            ba = absorb_best_attempts(addr, claim_id, packet)
        info, new, sk = fetch_rivals(api, addr, claim_id, seen, lane)
        return new, sk, ba

    def safe_harvest(addr, cid, keep, lane):
        """One bad checkpoint must not kill a 600-function run (the claim is still released)."""
        try:
            return harvest(addr, cid, keep, lane)
        except Exception as e:
            print("  [%s] %s harvest failed: %s" % (lane, addr, str(e)[:120]))
            log("error", address=addr, claim_id=cid, lane=lane, error=str(e)[:300])
            error("harvest_exception", addr, cid, "%s: %s" % (type(e).__name__, str(e)[:200]))
            return 0, 0, 0

    if not args.dry_run:                     # a dry run must not touch the rivals tree
        print("\n-- claims we already hold --")
        try:
            for addr, cid in live:
                new, sk, ba = harvest(addr, cid, ours_to_keep=True)
                imported += new
                dup += sk
                ba_added += ba
                print("  %s keep %s (not ours to release)" % (addr, cid))
                if (time.time() - t0) / 60.0 > args.max_minutes:
                    break
        except Budget:
            print("  budget exhausted while harvesting our live claims")

    if not args.live_only:
        defaults = {"sort": args.sort, "band": BANDS[0], "pool": "near",
                    "batch": args.batch, "max_functions": args.max_functions}
        if args.lane:
            lanes = [parse_lane(s, defaults) for s in args.lane]
        elif args.addresses.strip():
            addrs = [a.strip().lower() for a in args.addresses.split(",") if a.strip()]
            lanes = [Lane("addresses", BANDS[0], "any", "attempts", len(addrs), len(addrs), addrs)]
        else:
            # one lane per band: every band gets worked at once, and this is what the old
            # single-list default got wrong (it admitted only 512-1K and up)
            lanes = [Lane("near-" + b, b, "near", args.sort,
                          max(1, args.max_open // max(1, len(args.band))), args.max_functions,
                          min_give_ups=args.min_give_ups,
                          min_near_misses=args.min_near_misses) for b in args.band]
        print("\n-- %d lane(s), max %d claims open --" % (len(lanes), args.max_open))
        for L in lanes:
            print("  " + repr(L))
        # --jobs is a total: four lanes must not each spawn a full set of threads
        lane_jobs = max(1, args.jobs // max(1, len(lanes)))
        # a chunk must fit inside the claim ceiling, or the lane blocks waiting for a slot it
        # will only free after the chunk it is still filling (deadlock, seen with --addresses)
        for L in lanes:
            L.batch = max(1, min(L.batch, args.max_open // max(1, len(lanes))))
        print("  %d harvest threads per lane (%d total), %d score workers"
              % (lane_jobs, lane_jobs * len(lanes), args.score_jobs))

        SLOTS = None if args.keep else threading.Semaphore(args.max_open)
        RES_LOCK = threading.Lock()
        RESERVED = set()

        def run_lane(lane):
            """This lane's whole loop: pick its pool, claim a batch, harvest, give up."""
            nonlocal held
            out = {"lane": lane.name, "probed": 0, "new": 0, "dup": 0, "ba": 0}
            targets = lane.addresses or lane_targets(api, lane, args, held, idx)
            targets = targets[:lane.max_functions]
            print("\n[%s] %d targets" % (lane.name, len(targets)))
            if args.dry_run:
                print("  [%s] %s" % (lane.name, " ".join(targets[:25])))
                return out
            for i in range(0, len(targets), lane.batch):
                if (time.time() - t0) / 60.0 > args.max_minutes:
                    print("  [%s] time limit reached, stopping" % lane.name)
                    break
                chunk = targets[i:i + lane.batch]
                opened, refused = [], 0
                try:
                    # refresh the held set every batch: a function another agent (or another
                    # lane) claimed since the sweep started must never be probed
                    st2 = api.post("status", {})
                    held |= {c["address"].lower() for c in st2.get("open_claims") or []}
                    for a in chunk:
                        if a in held:
                            continue
                        with RES_LOCK:
                            if a in RESERVED:
                                continue
                            RESERVED.add(a)
                        if SLOTS is not None:
                            if not SLOTS.acquire(timeout=60):
                                break      # no free slot: harvest what we have, then continue
                        try:
                            r = api.post("claim", {"address": a, "model": "rivals_import",
                                                   "harness": "opencode", "effort": "none",
                                                   "prefer": "attempted"})
                        except Budget:
                            if SLOTS is not None:
                                SLOTS.release()
                            print("  [%s] budget exhausted while claiming" % lane.name)
                            break
                        cid = r.get("claim_id")
                        if not cid:
                            refused += 1
                            if r.get("__err") and r.get("__err") != 409:
                                error("claim_refused", a, "",
                                      "HTTP %s %s" % (r.get("__err"),
                                                      (r.get("body") or "")[:150]))
                            if SLOTS is not None:
                                SLOTS.release()
                            continue
                        remember(cid, a)
                        opened.append((a, cid))
                        held.add(a)
                    print("  [%s] %d claims open (refused %d), harvesting with %d threads"
                          % (lane.name, len(opened), refused, lane_jobs))
                    with ThreadPoolExecutor(max_workers=lane_jobs) as ex:
                        for (new, sk, ba) in ex.map(
                                lambda ac: safe_harvest(ac[0], ac[1], args.keep, lane.name),
                                opened):
                            out["new"] += new
                            out["dup"] += sk
                            out["ba"] += ba
                            out["probed"] += 1
                finally:
                    still_open = {c["claim_id"] for c in held_claims()["claims"]}
                    todo = [ac for ac in opened if ac[1] in still_open]
                    if not args.keep:
                        with ThreadPoolExecutor(max_workers=lane_jobs) as ex:
                            list(ex.map(lambda ac: release(api, ac[1], ac[0]), todo))
                        if SLOTS is not None:
                            for _ in todo:
                                SLOTS.release()
            return out

        probed = 0
        if args.lane_mode == "parallel":
            with ThreadPoolExecutor(max_workers=max(1, len(lanes))) as ex:
                results = list(ex.map(run_lane, lanes))
        else:
            results = [run_lane(L) for L in lanes]   # lane order = priority order
        for res in results:
            imported += res["new"]
            dup += res["dup"]
            ba_added += res["ba"]
            probed += res["probed"]
        print("\n  probed %d" % probed)

    if args.dry_run:
        print("\ndry run: %d API requests, nothing written" % api.used)
        return

    print("\n-- scoring (%d in parallel) --" % args.score_jobs)
    infos = scan_infos()
    with ThreadPoolExecutor(max_workers=max(1, args.score_jobs)) as ex:
        list(ex.map(lambda kv: finalize(kv[0], kv[1], packs, 1, seen), infos.items()))
    save(SEEN, seen)
    infos = scan_infos()        # last_scan_utc is set by fetch_rivals, only for the addresses
    save(INDEX, infos)          # this run actually touched - otherwise --max-age means nothing
    if args.prune:
        prune_drafts(infos)
    write_report(infos)
    write_structures()

    print("\nimported %d new rival files (%d already known, %d from the site's best attempts) | %d API requests | %.0fs"
          % (imported, dup, ba_added, api.used, time.time() - t0))
    print("report:   %s" % REPORT)
    print("code:     %s\\<address>\\best.cpp" % RIVALS)


if __name__ == "__main__":
    main()
