#!/usr/bin/env python3
"""PreToolUse hook: refuse `python3 - <<EOF` whose script reads sys.stdin.

WHY THIS EXISTS.

`python3 -` reads the PROGRAM from stdin. A heredoc feeds stdin. So a script delivered by
heredoc that then reads `sys.stdin` is reading its own (already-consumed) source, and gets
nothing. It does not error. It returns empty, every time, for every input.

That is the worst shape a bug can have: silent, total, and indistinguishable from a
legitimate empty answer.

Twice in one session, 2026-09-15, both in the beads citation tooling:

  * A resolver written as `python3 - "$URL" <<'PY' ... ids = sys.stdin ... PY` returned zero
    resolved ids for every bead. The gate then wrote 800 LIVE bead ids into its
    known-dead baseline. It was caught only by a contradiction — the same session had
    measured that the tracker resolved 3200 of 3200 ids, and both could not be true.
  * One hour later, after that fix was written up in a commit message, the IDENTICAL bug was
    written again in a second helper (`tracker_status`). There the empty return was
    indistinguishable from "tracker unreachable", which was a deliberate sentinel — so the
    failure mode impersonated a designed one.

THE FIX IS ALWAYS THE SAME: pass the data as a FILE PATH or ARGV, never on stdin.

    python3 - "$ids_file" <<'PY'
    import sys
    with open(sys.argv[1]) as fh:        # <- not sys.stdin
        ids = [l.strip() for l in fh]
    PY

Or put the script in a real file and pipe data to it, where stdin is genuinely free.

WHAT IS NOT BLOCKED: a heredoc script that never touches stdin (the overwhelmingly common
case), and a real script file reading stdin from a pipe (`cat x | python3 script.py`), which
is correct and unaffected.
"""
import json
import re
import sys

# `python3 -` / `python -` (optionally with args) whose program arrives via heredoc.
DASH_STDIN = re.compile(r"\bpython3?\b[^|;&\n]*\s-\s(?:[^|;&\n]*)?<<-?\s*'?\"?([A-Za-z_][A-Za-z0-9_]*)")

# Reading stdin from inside that script. `input()` is included: it is stdin by another name.
READS_STDIN = re.compile(r"sys\.stdin|(?<![\w.])input\s*\(|fileinput\.")

MESSAGE = (
    "BLOCKED: this runs `python3 -` with the script on a heredoc, and the script reads "
    "sys.stdin.\n\n"
    "`python3 -` takes the PROGRAM from stdin, and the heredoc IS stdin. So sys.stdin is "
    "already consumed: the read returns nothing, for every input, without erroring. It is "
    "silent and total, and it looks exactly like a legitimate empty result.\n\n"
    "This exact bug was written twice in one session (2026-09-15). The first time it put 800 "
    "live bead ids into a known-dead baseline; the second time its empty return was "
    "indistinguishable from a deliberate 'unreachable' sentinel.\n\n"
    "Pass the data as a FILE or ARGV instead:\n"
    "    python3 - \"$ids_file\" <<'PY'\n"
    "    import sys\n"
    "    with open(sys.argv[1]) as fh:      # not sys.stdin\n"
    "        ...\n"
    "    PY\n\n"
    "Or write the script to a real file, where stdin is actually free to carry data."
)


def heredoc_body(cmd: str, delim: str) -> str:
    """The text between a heredoc opener for `delim` and its terminator."""
    lines, out, collecting = cmd.split("\n"), [], False
    opener = re.compile(r"<<-?\s*'?\"?" + re.escape(delim) + r"'?\"?")
    for line in lines:
        if collecting:
            if line.strip() == delim:
                break
            out.append(line)
        elif opener.search(line):
            collecting = True
    return "\n".join(out)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:  # noqa: BLE001
        return 0  # never break the session
    if payload.get("tool_name") != "Bash":
        return 0
    cmd = (payload.get("tool_input") or {}).get("command") or ""

    for m in DASH_STDIN.finditer(cmd):
        body = heredoc_body(cmd, m.group(1))
        if READS_STDIN.search(body):
            print(MESSAGE, file=sys.stderr)
            return 2  # block, and show the reason to the model
    return 0


if __name__ == "__main__":
    sys.exit(main())
