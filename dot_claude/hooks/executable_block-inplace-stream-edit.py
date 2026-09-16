#!/usr/bin/env python3
"""PreToolUse hook: refuse in-place stream edits (sed -i, perl -pi, ...) in Bash.

WHY THIS EXISTS.

In-place stream editors are pattern-oriented and silent. They do not tell you whether the
pattern matched, they do not tell you how many times, and they have no idea what the file
means. Three failures in this workspace, all the same shape:

  * `sed -i 's|^  -ot "ngram=CPU" .*|  |'` on a shell script replaced the line with two spaces
    AND DROPPED ITS TRAILING BACKSLASH, terminating the command at `-ncmoe 48`. Context, flash
    attention, quantised KV, thread count and slot count were silently never passed. The server
    came up healthy on defaults and the only visible symptom was a VRAM number that did not
    match the configuration.
  * A `--comment` flag was passed positionally: 33 renames applied, 31 comments silently
    rejected, exit code 0.
  * A regex extractor keyed on one instruction shape reported "(none)" for a command that was
    plainly present in another shape, and that was recorded as a fact about the binary.

The alternatives are strictly better because they FAIL LOUDLY:

  * **Edit / the Edit tool** - exact string match, errors if not found or not unique.
  * **Write** - full replacement when you intend to rewrite the file.
  * **python3 with an assertion**, which is what to use when a shell pipeline is genuinely
    wanted:
        s = p.read_text()
        assert old in s, "pattern not found"       # <- the whole point
        p.write_text(s.replace(old, new))
  * **`tools/redit`** for files on another host: fetch, exact-replace with assertion, verify,
    push back.

Non-in-place uses of sed/awk/perl (filtering a stream, `sed -n`, piping to a new file) are
untouched: the hazard is editing a file in place without verification, not the tools.
"""
import json
import re
import sys

# In-place edit invocations. Deliberately narrow: only forms that write back to a file.
PATTERNS = [
    (re.compile(r"\bsed\b[^|;&\n]*\s-[a-zA-Z]*i\b"), "sed -i"),
    # `perl -pi -e` puts both letters in ONE flag cluster, so a rule that expects two separate
    # flags misses the most common form. Match any perl invocation whose flag clusters contain
    # both `i` and one of `p`/`n`, in either order and in either one or two clusters.
    (re.compile(r"\bperl\b(?=[^|;&\n]*\s-[a-zA-Z]*i)(?=[^|;&\n]*\s-[a-zA-Z]*[pn])"), "perl -pi/-ni"),
    (re.compile(r"\bgawk\b[^|;&\n]*-i\s+inplace"), "gawk -i inplace"),
    (re.compile(r"\bruby\b(?=[^|;&\n]*\s-[a-zA-Z]*i)(?=[^|;&\n]*\s-[a-zA-Z]*[pn])"), "ruby -pi"),
]

MESSAGE = (
    "BLOCKED: {what} edits a file in place by pattern and cannot tell you whether it matched, "
    "how many times, or that it just broke a line continuation. That exact failure has "
    "happened three times in this workspace.\n\n"
    "Use instead:\n"
    "  * the Edit tool - exact string, errors if not found or not unique\n"
    "  * the Write tool - when you mean to rewrite the whole file\n"
    "  * python3 with an assertion:\n"
    "        s = p.read_text(); assert old in s, 'pattern not found'\n"
    "        p.write_text(s.replace(old, new))\n"
    "  * tools/redit <host> <path> - for a file on another machine (fetch, assert, verify, push)\n\n"
    "Streaming uses are fine: `sed -n`, `sed ... > new_file`, sed in a pipe. Only the in-place "
    "write is refused."
)


def strip_heredocs(cmd: str) -> str:
    """Remove heredoc BODIES before matching.

    This hook blocked its own author writing documentation: a `cat > file <<'EOF'` whose body
    explained the sed failure contained the literal string `sed -i`, and the hook matched it.
    A heredoc body is data, not a command. Matching it is a false positive, and a hook that
    cries wolf gets disabled, which is worse than not having it.
    """
    out, lines, i = [], cmd.split("\n"), 0
    delim_rx = re.compile(r"<<-?\s*'?\"?([A-Za-z_][A-Za-z0-9_]*)'?\"?")
    while i < len(lines):
        line = lines[i]
        out.append(line)
        m = delim_rx.search(line)
        i += 1
        if not m:
            continue
        end = m.group(1)
        while i < len(lines) and lines[i].strip() != end:
            i += 1                                               # skip the body entirely
        if i < len(lines):
            i += 1                                               # and the terminator
    return "\n".join(out)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:                                            # noqa: BLE001
        return 0                                                 # never break the session
    if payload.get("tool_name") != "Bash":
        return 0
    cmd = strip_heredocs((payload.get("tool_input") or {}).get("command") or "")
    for rx, what in PATTERNS:
        if rx.search(cmd):
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": MESSAGE.format(what=what),
                }
            }))
            return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
