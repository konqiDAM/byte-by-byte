"""add_sessions.py - append agent rows to sessions.md before launching (AGENTS.md rule: no saved id = no way to stop it).

    python exp91/add_sessions.py <file-with-rows>

Each line of the file is appended verbatim. Kept trivial on purpose.
"""
import io
import sys

P = r"C:\f3decomp\sessions.md"


def main():
    rows = io.open(sys.argv[1], encoding="utf-8").read().rstrip()
    with io.open(P, "a", encoding="utf-8", newline="\n") as fh:
        fh.write("\n" + rows + "\n")
    print("appended %d line(s) to sessions.md" % len(rows.splitlines()))


if __name__ == "__main__":
    main()
