#!/usr/bin/env python3
"""PostToolUse hook: say so when a Bash command ABORTED instead of running.

WHY THIS EXISTS.

zsh's default `nomatch` makes an unmatched glob a FATAL error for the whole command line.
The command never runs. What comes back is one error line — and an error line read quickly
looks like a result, especially a result that says "nothing found", which is exactly the
answer a search was hoping for.

Measured 2026-09-15:

    grep -rn 'beads-env' ~/.zshrc ~/.zshenv ~/.bashrc ~/.profile ~/.config/zsh/* 2>/dev/null
    (eval):2: no matches found: /home/brian/.config/zsh/*

`~/.config/zsh/` did not exist, zsh aborted before grep ran, and that was recorded as
"nothing sources ~/.beads-env". Both ~/.zshrc and ~/.zshenv source it, on the lines that
grep would have printed. The wrong conclusion stood for several turns and was corrected only
because a later command happened to look again.

This is the "a search that returns nothing is evidence about the search" rule failing in its
least visible form: not a pattern that matched nothing, but a command that never executed.

WHAT THIS DOES: appends a short warning when the output carries a shell-abort marker, so the
absence cannot be read as an answer. It does not block anything.

Deliberately NARROW. `No such file or directory` and ordinary non-zero exits are not flagged:
they are everyday, usually expected, and a hook that cries wolf gets turned off — which is
worse than no hook. Only markers that mean THE COMMAND DID NOT RUN are listed.
"""
import json
import re
import sys

ABORTS = [
    (re.compile(r"no matches found:", re.I), "zsh aborted on an unmatched glob"),
    (re.compile(r"bad pattern:", re.I), "zsh aborted on a malformed glob"),
    (re.compile(r"^\(eval\):\d+: command not found", re.M), "the command name did not resolve"),
    (re.compile(r"parse error near", re.I), "the shell failed to parse the command"),
]

NOTE = (
    "\n\n[hook] SHELL ABORT — {why}. The command did NOT run, so this output is not a "
    "result and an empty or partial answer here means nothing. Re-run it with the offending "
    "argument quoted or removed (quote globs, or test the path first) before drawing any "
    "conclusion — especially a conclusion that something is ABSENT."
)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:  # noqa: BLE001
        return 0
    if payload.get("tool_name") != "Bash":
        return 0
    resp = payload.get("tool_response")
    text = ""
    if isinstance(resp, str):
        text = resp
    elif isinstance(resp, dict):
        text = " ".join(
            str(resp.get(k) or "") for k in ("stdout", "stderr", "output", "error")
        )
    if not text:
        return 0
    for rx, why in ABORTS:
        if rx.search(text):
            print(NOTE.format(why=why), file=sys.stderr)
            return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
