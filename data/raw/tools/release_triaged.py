"""release_triaged.py - release the triaged twins that are blocked or hopeless, keeping best_code.

    python exp91/release_triaged.py

Triaged 2026-11-14 from the high-give-up twin list. Verdicts and reasons live here so the release carries the analysis
rather than a shrug.
"""
import io
import json
import os
import time
import urllib.error
import urllib.request

API = "https://f3decomp.com/api/v1/"
KEY = io.open(os.path.expanduser(r"~\.f3decomp_key"), encoding="utf-8").read().strip()
MODEL = "DeepSeek V4.1 Flash"
ROOT = r"C:\f3decomp"

JOBS = [
    ("0x00953a90", "clm_4fe444cdad5940c18454", "pack_problem",
     "66 give-ups but the stored draft scores 0 in the pack: it MATCHES the pack and is refused by the project file, "
     "because the pack scaffold class FUN_00cd1780 carries an extra bool between m_pServer and the first hkArray, "
     "shifting every array member by 4 bytes. Confirmed pack_problem already open; the same scaffold refuses drafts at "
     "0x00afd570 and 0x009b6cf0. Nothing to author until the pack is fixed.",
     "pack matches, project file refuses: scaffold member shifted by 4 bytes",
     "pack scaffold defect (extra bool), not a source problem", None),
    ("0x004fcbb0", "clm_037e9fa0b40c45d88630", "pack_problem",
     "the pack lacks the documented fnv_FloatToInt helper that the texture-grid conversions require (open pack_problem) - "
     "the same class of defect that has 0x009925d0 paused. Best saved attempt 14102, extent 2288 vs 2352 from byte 0.",
     "extent 2288 vs 2352, first difference at byte 0 (frame shape)",
     "missing helper header in the pack", None),
    ("0x009cb440", "clm_a8df9259d47c4eec80d1", "out_of_time",
     "49 of the 53 give-ups are screening passes; the two real attempts are orchestrator time-limit releases with best "
     "scores 12354 and 74315. Nobody has been close, at 2755 bytes with 2 near misses - the count is farmed, not "
     "difficulty, and the size makes it a 3-lease job from nothing.",
     "no measured residue - nothing close",
     "no attempt ever reached a structural draft", None),
    ("0x0091f230", "clm_cecc947d099d4f3aa608", "other",
     "best saved attempts 50559 and 82128; the drafts compile to 11, 251 and 1399 bytes against 2929 - i.e. nobody has "
     "written the body at all. Also /Od-labelled while the file is almost certainly /O2 (same region as the flagged "
     "units), so a match would need a compile_flags proof as well.",
     "nothing structural; drafts are stubs",
     "no work done by anyone (best score 50559)", None),
]


def post(path, payload=None):
    r = urllib.request.Request(API + path, data=json.dumps(payload or {}).encode(),
                               headers={"Authorization": "Bearer " + KEY,
                                        "User-Agent": "Mozilla/5.0",
                                        "Content-Type": "application/json"})
    for _ in range(3):
        try:
            return json.loads(urllib.request.urlopen(r).read().decode() or "{}")
        except urllib.error.HTTPError as e:
            return {"ERR": e.code, "body": e.read().decode("utf-8", "replace")[:250]}
        except Exception:
            time.sleep(2)
    return {"ERR": "retry"}


def main():
    for addr, cid, cat, tried, differs, cause, best in JOBS:
        code = ""
        if best and os.path.exists(best):
            code = io.open(best, encoding="utf-8", errors="replace").read()
        r = post("giveup", {"claim_id": cid, "category": cat, "tried": tried,
                            "still_differs": differs, "suspected_cause": cause,
                            "best_code": code, "model": MODEL})
        print("%-12s %s -> %s" % (addr, cid, json.dumps(r)[:110]))


if __name__ == "__main__":
    main()
