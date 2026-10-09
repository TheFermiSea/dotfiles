#!/usr/bin/env python3
"""PreToolUse hook: refuse Bash commands whose nested quoting is already broken, before they run.

WHY THIS EXISTS.

Code nested inside quoted strings - Python inside `ssh host '...'`, sed inside
`pct exec 102 -- bash -c "..."`, a heredoc written by `cat > x.py <<"PY"` inside an ssh
string - passes through one shell per layer, and each layer rewrites quotes, backslashes
and `$`. The mangling only shows when the command runs, often as a SyntaxError on the far
side, sometimes not at all: on 2026-10-09 a serial-console capture was launched with
nohup, died on a SyntaxError that nobody saw, and a one-time switch power cycle went
unrecorded. In that session 11 of 886 Bash calls failed this way, and 9 more on zsh's
"no matches found" for unquoted globs.

A static parser catches all of these exactly; a language model does not (Jev scored
AUC 0.57/0.69 on the same 22 commands). So this hook only blocks what it can PROVE:

  1. `zsh -n` on the whole command (the tool's shell) fails.
  2. A command string handed to another shell - the remote command of `ssh`, the argv
     after `--` of `pct exec`, the string after `-c` of bash/sh/zsh - fails `bash -n`.
     Checked recursively, layer by layer.
  3. Embedded Python does not compile: `python3 -c STRING`, a `python3 - <<DELIM` body,
     or a `cat > something.py <<DELIM` body, at any layer.
  4. zsh-only traps: an unquoted word with glob characters that matches nothing (zsh
     aborts with "no matches found"); assigning or looping over zsh's special parameters
     (`path` is tied to PATH: `for path in ...` wipes the command search path, `status` is
     read-only); `pkill -f`/`pkill -f` patterns that also match the shell running them.

Everything else passes. Any internal error fails OPEN (the command runs) and is logged.
Decisions are logged to ~/.local/state/shell-guard/decisions.jsonl.

THE FIX IS ALWAYS THE SAME: put the code in a file, syntax-check it locally, ship it.
    remote-run HOST script.py|script.sh [args]     # ssh host
    remote-run HOST/CTID script.sh [args]          # pct exec CTID on HOST
"""
import glob
import json
import os
import re
import shlex
import subprocess
import sys
import time

LOG = os.path.expanduser("~/.local/state/shell-guard/decisions.jsonl")
SHELLS = {"bash", "sh", "zsh", "dash"}
PYTHONS = re.compile(r"^python(3(\.\d+)?)?$")
SSH_OPTS_WITH_ARG = set("BbcDEeFIiJLlmOoPpQRSWw")
ZSH_SPECIAL = ("path", "status", "argv", "cdpath", "fpath", "manpath", "module_path", "pipestatus")
CONTROL = {";", "&&", "||", "|", "&", "|&", ";;", "(", ")", "\n"}


def _syntax(shell, text):
    """Return an error string if `shell -n` rejects text, else None."""
    try:
        r = subprocess.run([shell, "-n"], input=text, capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if r.returncode != 0:
        return (r.stderr or r.stdout).strip().splitlines()[0][:300] if (r.stderr or r.stdout).strip() else "syntax error"
    return None


def _py(text, where):
    try:
        compile(text, where, "exec")
    except SyntaxError as e:
        return f"{where}: Python SyntaxError line {e.lineno}: {e.msg}: {(e.text or '').strip()[:120]}"
    return None


def split_heredocs(text):
    """Return (text_without_heredoc_bodies, [(opener_line, delim, quoted, body)]), quote-aware."""
    out, docs, i, n = [], [], 0, len(text)
    pending = []  # (opener_line_start, delim, quoted)
    quote = None
    line_start = 0
    while i < n:
        c = text[i]
        if quote:
            if c == "\\" and quote == '"' and i + 1 < n:
                out.append(text[i:i + 2]); i += 2; continue
            if c == quote:
                quote = None
            out.append(c); i += 1; continue
        if c == "\\" and i + 1 < n:
            out.append(text[i:i + 2]); i += 2; continue
        if c in ("'", '"'):
            quote = c; out.append(c); i += 1; continue
        if c == "#" and (i == 0 or text[i - 1] in " \t\n;"):
            j = text.find("\n", i)
            j = n if j < 0 else j
            out.append(text[i:j]); i = j; continue
        m = re.match(r"<<(?!<)-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1", text[i:])
        if m:
            pending.append((line_start, m.group(2), bool(m.group(1))))
            out.append(m.group(0)); i += m.end(); continue
        if c == "\n":
            out.append(c); i += 1
            for (ls, delim, quoted) in pending:
                body = []
                while i < n:
                    j = text.find("\n", i)
                    line = text[i:] if j < 0 else text[i:j]
                    i = n if j < 0 else j + 1
                    if line.strip() == delim:
                        break
                    body.append(line)
                opener = text[ls:text.find("\n", ls) if text.find("\n", ls) >= 0 else n]
                docs.append((opener, delim, quoted, "\n".join(body)))
            pending = []
            line_start = i
            continue
        out.append(c); i += 1
    return "".join(out), docs


def _dq_escapes(text):
    """Pre-apply the POSIX double-quote escapes shlex omits: inside "...", `\\$` and `\\``
    lose the backslash (shlex only handles `\\"` and `\\\\`). Placeholders survive shlex and
    are restored by _undo_dq."""
    out, q, i = [], None, 0
    while i < len(text):
        c = text[i]
        if q == "'":
            if c == "'":
                q = None
        elif c == "\\" and i + 1 < len(text):
            nxt = text[i + 1]
            if q == '"' and nxt in "$`":
                out.append("\x03" if nxt == "$" else "\x04"); i += 2; continue
            out.append(text[i:i + 2]); i += 2; continue
        elif c in ("'", '"'):
            q = None if q == c else (c if q is None else q)
        out.append(c); i += 1
    return "".join(out)


def _undo_dq(s):
    return s.replace("\x03", "$").replace("\x04", "`")


def simple_commands(text):
    """Split shell text (heredoc bodies removed) into argv lists, POSIX quote removal applied.

    Redirections (`2>&1`, `>/dev/null`, `< f`, `<<DELIM`, `<<< str`) are dropped together with
    their target, so they never leak into a payload handed to another shell.
    """
    lex = shlex.shlex(_dq_escapes(text), posix=True, punctuation_chars=";&|()<>")
    lex.whitespace_split = True
    lex.commenters = "#"
    toks = list(lex)
    cmds, cur, k = [], [], 0
    while k < len(toks):
        tok = toks[k]
        if set(tok) <= set(";&|()<>"):
            if "<" in tok or ">" in tok:
                if cur and cur[-1].isdigit():
                    cur.pop()  # the fd number of `2>`
                k += 2  # the operator and its target
                continue
            if cur:
                cmds.append(cur)
            cur = []
        else:
            cur.append(_undo_dq(tok))
        k += 1
    if cur:
        cmds.append(cur)
    return cmds


def _strip_prefix(argv):
    """Drop env assignments, `sudo`, `timeout N`, `nohup`, `exec`, `command`, `env` prefixes."""
    i = 0
    while i < len(argv):
        a = argv[i]
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", a) or a in ("nohup", "exec", "command", "builtin", "nice", "time", "env"):
            i += 1
        elif a == "sudo":
            i += 1
            while i < len(argv) and argv[i].startswith("-"):
                i += 1
        elif a in ("timeout", "gtimeout"):
            i += 1
            while i < len(argv) and argv[i].startswith("-"):
                i += 1
            i += 1  # duration
        else:
            break
    return argv[i:]


def nested_payloads(argv):
    """Yield (kind, payload) for strings this argv hands to another interpreter."""
    argv = _strip_prefix(argv)
    if not argv:
        return
    prog = os.path.basename(argv[0])
    if prog == "ssh":
        i = 1
        while i < len(argv) and argv[i].startswith("-") and argv[i] != "--":
            flag = argv[i]
            i += 2 if (len(flag) == 2 and flag[1] in SSH_OPTS_WITH_ARG) else 1
        if i < len(argv) and argv[i] == "--":
            i += 1
        rest = argv[i + 1:]
        if rest:
            yield "shell", " ".join(rest)
    elif prog == "pct" and len(argv) > 2 and argv[1] == "exec":
        if "--" in argv:
            inner = argv[argv.index("--") + 1:]
            yield from nested_payloads(inner)
    elif prog in SHELLS:
        if "-c" in argv and argv.index("-c") + 1 < len(argv):
            yield "shell", argv[argv.index("-c") + 1]
    elif PYTHONS.match(prog):
        # `-c` is python's only if it comes before the script path / `-` / `-m`
        for k, a in enumerate(argv[1:], 1):
            if a == "-c" and k + 1 < len(argv):
                yield "python", argv[k + 1]
                break
            if a in ("-", "-m") or not a.startswith("-"):
                break


ZSH_GLOB = re.compile(r"[*?]|\[[^\]]*\]")


def _sub_end(text, i):
    """Index just past the `)` closing the $( opened at text[i] (quote-aware, single pass)."""
    depth, j, q, n = 1, i + 2, None, len(text)
    while j < n and depth:
        ch = text[j]
        if q:
            if ch == "\\" and q == '"':
                j += 1
            elif ch == q:
                q = None
        elif ch == "\\":
            j += 1
        elif ch in ("'", '"'):
            q = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        j += 1
    return j


def mask_quotes_and_subs(text):
    """Return (masked, substitutions).

    masked: `text` with every quoted span replaced by \x01 and every $( ... ) or
    backtick substitution replaced by \x02 (same length, so word boundaries hold).
    substitutions: the inner text of each $( ... ) / backtick span, to be checked on its own -
    zsh globs inside a substitution even when the substitution sits inside double quotes.
    """
    out, subs, i, n = [], [], 0, len(text)
    while i < n:
        c = text[i]
        if c == "\\" and i + 1 < n:
            out.append("\x01\x01"); i += 2; continue
        if c == "'" or (c == "$" and text[i + 1:i + 2] == "'"):
            j = text.find("'", i + (2 if c == "$" else 1))
            j = n - 1 if j < 0 else j
            out.append("\x01" * (j - i + 1)); i = j + 1; continue
        if c == "$" and text[i + 1:i + 2] == "(" and text[i + 2:i + 3] != "(":
            j = _sub_end(text, i)
            subs.append(text[i + 2:j - 1])
            out.append("\x02" * (j - i)); i = j; continue
        if c == "`":
            j = text.find("`", i + 1)
            j = n - 1 if j < 0 else j
            subs.append(text[i + 1:j])
            out.append("\x02" * (j - i + 1)); i = j + 1; continue
        if c == '"':
            j, buf = i + 1, ["\x01"]
            while j < n and text[j] != '"':
                if text[j] == "\\" and j + 1 < n:
                    buf.append("\x01\x01"); j += 2; continue
                if text[j] == "$" and text[j + 1:j + 2] == "(" and text[j + 2:j + 3] != "(":
                    k = _sub_end(text, j)
                    subs.append(text[j + 2:k - 1])
                    buf.append("\x01" * (k - j)); j = k; continue
                buf.append("\x01"); j += 1
            out.append("".join(buf) + "\x01"); i = j + 1; continue
        if c == "#" and (i == 0 or text[i - 1] in " \t\n;&|("):
            j = text.find("\n", i)
            j = n if j < 0 else j
            out.append(" " * (j - i)); i = j; continue
        out.append(c); i += 1
    return "".join(out), subs


def zsh_traps(text, depth=0):
    """zsh-only failure classes, checked on text outside quotes (heredoc bodies already removed)."""
    problems = []
    if depth > 4 or re.search(r"\bsetopt\s+(null_?glob|no_?nomatch|no_?glob)\b", text, re.I):
        return problems
    masked, subs = mask_quotes_and_subs(text)
    for inner in subs:
        problems += zsh_traps(inner, depth + 1)
    env = {"HOME": os.path.expanduser("~")}
    for m in re.finditer(r"(?:^|[;&|\s])(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)=([^\s;&|'\"$`()]*)(?=[\s;&|]|$)", text):
        env[m.group(1)] = m.group(2)
    changes_dir = bool(re.search(r"(^|[;&|(\s])(cd|pushd)\s", masked))
    words = re.split(r"[\s;&|()<>]+", masked)
    raw_pos = 0
    for w in words:
        start = masked.find(w, raw_pos) if w else raw_pos
        raw_pos = start + len(w)
        if not w or "\x01" in w or set(w) <= {"\x02"}:
            continue  # quoted text, or a whole substitution
        if masked[raw_pos:raw_pos + 2].lstrip()[:1] == ")":
            continue  # a `case` pattern (`*ACTIVE*)`), not a file glob
        if not ZSH_GLOB.search(w) or w in ("[", "]", "[[", "]]") or re.fullmatch(r"\[\[?.*", w):
            continue
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", w):
            continue  # an assignment: zsh does not glob the right-hand side
        word = text[start:start + len(w)]
        expanded = re.sub(r"\$\{?([A-Za-z_][A-Za-z0-9_]*)\}?", lambda m: env.get(m.group(1), "\0"), word)
        if "\0" in expanded or "\x02" in w:
            continue  # depends on a value only known at run time
        expanded = os.path.expanduser(expanded.replace("\\", ""))
        if expanded.startswith("-"):
            pass  # `--include=*.md` is globbed as a whole word: it can never match a file
        elif changes_dir and not expanded.startswith("/"):
            continue  # relative to a directory this command cds into; cannot evaluate here
        if not glob.glob(expanded):
            problems.append(f"unquoted glob `{word}` matches nothing; zsh aborts the WHOLE command with "
                            f"'no matches found' (quote it if it is a pattern for the tool: '{word}')")
    for m in re.finditer(r"(?:^|[;&|(\s])(?:for\s+)?(" + "|".join(ZSH_SPECIAL) + r")(=|\s+in\s)", masked):
        problems.append(f"`{m.group(1)}` is a zsh special parameter ({'tied to PATH' if m.group(1) == 'path' else 'reserved'}); "
                        f"assigning or looping over it breaks the shell - use another name")
    return list(dict.fromkeys(problems))


def pkill_self(argv):
    argv = _strip_prefix(argv)
    if argv and os.path.basename(argv[0]) == "pkill" and "-f" in argv:
        pats = [a for a in argv[1:] if not a.startswith("-")]
        if pats and not re.search(r"\[[^\]]+\]", pats[-1]):
            return (f"`pkill -f {pats[-1]}` also matches the shell running this command (its own command "
                    f"line contains the pattern) and kills it mid-command; write the pattern as "
                    f"'[{pats[-1][:1]}]{pats[-1][1:]}' or kill by PID")
    return None


def check_shell(text, shell, where, depth=0):
    problems = []
    if depth > 6:
        return problems
    if shell != "zsh":  # the top level was already checked with zsh in evaluate()
        err = _syntax(shell, text)
        if err:
            problems.append(f"{where}: `{shell} -n` rejects it: {err}")
            return problems
    body_free, docs = split_heredocs(text)
    for opener, delim, quoted, body in docs:
        # only the simple command that owns this heredoc: the opener line up to `<<DELIM`,
        # after the last control operator
        head = re.split(r"<<-?\s*['\"]?" + re.escape(delim), opener, maxsplit=1)[0]
        o = re.split(r"&&|\|\||[;|&]", head)[-1].strip()
        if re.search(r"\bpython3?(\.\d+)?\b(\s+\S+)*\s+-(\s+\S+)*\s*$|\bpython3?(\.\d+)?\s*$", o):
            if quoted:  # an unquoted delimiter means the shell expands $VARS first; only check what we know
                e = _py(body, f"{where}: python heredoc <<{delim}")
                if e:
                    problems.append(e)
        elif re.search(r"\bcat\s*>\s*\S+\.py['\"]?\s*$|\btee\s+\S+\.py['\"]?\s*$", o):
            e = _py(body, f"{where}: {o[:60]}")
            if e:
                problems.append(e)
        elif re.search(r"\b(bash|sh)\s+-s\b.*$|\bcat\s*>\s*\S+\.sh['\"]?\s*$", o):
            err = _syntax("bash", body)
            if err:
                problems.append(f"{where}: shell heredoc <<{delim}: `bash -n` rejects it: {err}")
    try:
        cmds = simple_commands(body_free)
    except ValueError:
        return problems  # the real shell's -n already accepted this layer; shlex is the weaker parser
    for argv in cmds:
        p = pkill_self(argv) if depth == 0 else None  # proven locally (exit 144); remote shells survived it
        if p:
            problems.append(f"{where}: {p}")
        for kind, payload in nested_payloads(argv):
            label = f"{where} > {os.path.basename(_strip_prefix(argv)[0])}"
            if kind == "python":
                e = _py(payload, f"{label} -c")
                if e:
                    problems.append(e)
            else:
                problems += check_shell(payload, "bash", label, depth + 1)
    return problems


# `zsh -n` (NO_EXEC) cannot know what an expansion in command position runs, so it rejects
# `$PY - <<X ...` with "redirection with no command" although the command runs fine. Only
# messages that mean a real parse failure are trusted.
ZSH_FATAL = re.compile(r"parse error|unmatched|bad (pattern|substitution|math)|not found|unknown file attribute")


def evaluate(cmd):
    problems = []
    err = _syntax("zsh", cmd)
    if err and ZSH_FATAL.search(err):
        return [f"top level: `zsh -n` rejects it: {err}"]
    body_free, _ = split_heredocs(cmd)
    problems += [f"top level: {p}" for p in zsh_traps(body_free)]
    problems += check_shell(cmd, "zsh", "top level")
    # the top-level syntax check ran with zsh; check_shell re-runs it harmlessly
    return list(dict.fromkeys(problems))


MESSAGE = """BLOCKED (static check, nothing was run): this command would fail or run different code than written.

{problems}

Nested quoting is the cause in almost every case: each shell layer (zsh here, then ssh's
remote shell, then bash -c ...) rewrites quotes, backslashes and $ in the code inside it.
Do not repair it by adding escapes. Put the code in a file instead:
  1. Write the script with the Write tool (no shell quoting involved).
  2. Run it with:  remote-run HOST script.sh|script.py [args]    (or HOST/CTID for pct exec)
     remote-run syntax-checks it locally (bash -n / py_compile), copies it, runs it, cleans up.
For zsh globs, quote patterns meant for the tool ('*.py'), not for the shell."""


def log(entry):
    try:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except OSError:
        pass


def main():
    try:
        data = json.load(sys.stdin)
        cmd = (data.get("tool_input") or {}).get("command") or ""
    except Exception:  # noqa: BLE001 - malformed input: fail open
        return 0
    t0 = time.time()
    try:
        problems = evaluate(cmd)
    except Exception as e:  # noqa: BLE001 - a guard bug must never block work
        log({"ts": time.time(), "decision": "error", "error": repr(e)[:300], "cmd": cmd[:400]})
        return 0
    log({"ts": time.time(), "decision": "deny" if problems else "allow", "ms": round((time.time() - t0) * 1000),
         "problems": problems, "cmd": cmd[:400] if problems else None})
    if problems:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse", "permissionDecision": "deny",
            "permissionDecisionReason": MESSAGE.format(problems="\n".join(f"  - {p}" for p in problems))}}))
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--evaluate":  # test entry: evaluate a command from a file
        print(json.dumps(evaluate(open(sys.argv[2]).read())))
    else:
        sys.exit(main())
