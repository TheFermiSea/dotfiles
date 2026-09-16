#!/usr/bin/env python3
"""PreToolUse hook: refuse a paginated `bd` listing piped into a line filter.

WHY THIS EXISTS.

`bd ready` prints at most 100 rows by default and says so, on its LAST line:

    Showing 100 of 490 ready issues. Use -n to show more.

That footer is the only thing distinguishing "there are no more" from "there are
390 more". Pipe the command into `grep`/`rg` and the footer is the first thing
discarded, because it does not match the pattern. What comes back is silence, and
silence reads as absence.

Measured 2026-09-16. `bd ready | rg 'pt6ic'` returned nothing, and that was
reported to the operator as the bead being invisible. The bead was real, open,
synced, and ranked #207 of 490 — it was simply below the fold, and the line that
said so had been filtered away by the same command that "looked" for it.

The tool was not at fault. bd reported its own truncation accurately. The filter
destroyed the report and the absence was then read as an answer.

THE FIX IS ALWAYS ONE OF TWO THINGS:

    bd ready --limit 0 | rg 'pt6ic'     # ask for the whole list, then filter
    bd show <id>                        # or address the thing directly

WHAT IS NOT BLOCKED: any listing with an explicit `-n`/`--limit` (you have
already thought about the bound), `--json` output (machine-readable, and the
caller is parsing rather than eyeballing), `bd show`, and every non-listing
command. Piping to a pager or to `cat` is fine — those do not drop lines.

Deliberately narrow: a hook that cries wolf gets disabled, which is worse than
not having it.
"""
import json
import re
import sys

# bd subcommands that page and print a "Showing N of M" footer.
PAGINATED = r"(?:ready|list|blocked|search|children|stale|memories|duplicates|find-duplicates)"

# `bd <sub> ...` piped into something that drops non-matching lines.
LINE_FILTER = r"(?:grep|rg|ag|ack|egrep|fgrep)\b"
PIPED = re.compile(
    rf"\bbd\b(?:\s+-C\s+\S+)?\s+{PAGINATED}\b([^|]*)\|\s*{LINE_FILTER}",
)

# An explicit bound means the author already reasoned about the limit.
HAS_LIMIT = re.compile(r"(?:^|\s)(?:-n|--limit)(?:[=\s]|$)")
IS_JSON = re.compile(r"(?:^|\s)--json(?:\s|$)")

MESSAGE = (
    "BLOCKED: this pipes a paginated `bd` listing into a line filter.\n\n"
    "`bd ready` and friends cap their output (100 rows by default) and report it "
    "on the LAST line:\n"
    "    Showing 100 of 490 ready issues. Use -n to show more.\n\n"
    "A grep/rg filter discards that footer first, because it does not match the "
    "pattern. An empty result then looks exactly like 'not there' when it may "
    "mean 'not in the first 100'.\n\n"
    "This happened on 2026-09-16: `bd ready | rg 'pt6ic'` returned nothing and was "
    "reported as the bead being invisible. It was real, open, synced, and ranked "
    "#207 of 490.\n\n"
    "Use one of:\n"
    "    bd ready --limit 0 | rg 'pt6ic'   # bound it yourself, then filter\n"
    "    bd show <id>                      # or address it directly\n\n"
    "An explicit -n/--limit, or --json, is not blocked."
)


# Heredoc bodies are DATA, not commands: a commit message, a PR body or a doc
# that quotes the bad pattern must not be blocked by the hook that exists to
# describe it. This is not hypothetical — the first live run of this hook refused
# the commit that introduced it, because the message quotes
# `bd ready | rg 'pt6ic'` as the incident it documents. The sibling hook
# block-inplace-stream-edit.py carries the same rule for the same reason.
HEREDOC_OPEN = re.compile(r"<<-?\s*'?\"?([A-Za-z_][A-Za-z0-9_]*)'?\"?")


def strip_heredocs(cmd: str) -> str:
    """The command with every heredoc body removed, openers kept."""
    out, skip_until = [], None
    for line in cmd.split("\n"):
        if skip_until is not None:
            if line.strip() == skip_until:
                skip_until = None
            continue
        out.append(line)
        m = HEREDOC_OPEN.search(line)
        if m:
            skip_until = m.group(1)
    return "\n".join(out)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:  # noqa: BLE001
        return 0  # never break the session
    if payload.get("tool_name") != "Bash":
        return 0
    cmd = strip_heredocs((payload.get("tool_input") or {}).get("command") or "")

    for m in PIPED.finditer(cmd):
        flags = m.group(1)
        if HAS_LIMIT.search(flags) or IS_JSON.search(flags):
            continue
        print(MESSAGE, file=sys.stderr)
        return 2  # block, and show the reason to the model
    return 0


if __name__ == "__main__":
    sys.exit(main())
