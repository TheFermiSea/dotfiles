#!/usr/bin/env bash
#
# Register the guard hooks in ~/.claude/settings.json on every machine.
#
# WHY THIS EXISTS
#
# chezmoi carries the hook SCRIPTS. It deliberately does not carry
# ~/.claude/settings.json (.chezmoiignore), because that file also holds this
# host's permissions, model, statusLine and plugin set — ai-proxy denies the
# native Grep and Glob tools there, and no other machine should inherit that.
#
# But the hook REGISTRATION lives in settings.json. So a hook added here reached
# every machine as a file and fired on exactly one of them. Measured 2026-09-16:
# three guard hooks were registered on ai-proxy, none of those registrations
# existed anywhere else, and block-inplace-stream-edit.py — written after `sed -i`
# silently corrupted files three times — was not even distributed as a file.
# "Installed on every machine" was true of the bytes and false of the enforcement.
#
# This is chezmoi's answer to exactly that shape: converge state in a file you do
# not own. It runs after apply, only when this script's own content changes.
#
# WHAT IT WILL NOT DO
#
#   * It never removes, reorders or edits an entry it did not add. Anything
#     already in settings.json is left byte-identical.
#   * It never registers a hook whose script is absent on this machine — a
#     registration pointing at nothing makes every matching tool call log an
#     error, which is worse than no hook.
#   * It never writes a hard-coded /home/brian. Paths are built from $HOME, so
#     the macOS /Users/brian layout is correct rather than accidentally broken.
#   * It fails SOFT. An unreadable or unparseable settings.json is reported and
#     skipped, never overwritten: breaking a machine's Claude Code to install a
#     guard hook is a bad trade.
#
# To add a hook to the fleet: put the script under ~/.claude/hooks/, `chezmoi add`
# it, and add one row to HOOKS below. Editing this file is what makes chezmoi
# re-run it on the other machines.
set -uo pipefail

# event|matcher|script-basename        (matcher empty = fires for every tool)
HOOKS="
PreToolUse|Bash|block-inplace-stream-edit.py
PreToolUse|Bash|block-heredoc-stdin-collision.py
PreToolUse|Bash|block-filtered-paginated-listing.py
PostToolUse|Bash|flag-shell-abort-read-as-result.py
"

settings="${HOME}/.claude/settings.json"
hooks_dir="${HOME}/.claude/hooks"

[ -f "$settings" ] || { echo "register-claude-hooks: no $settings on this machine; nothing to do"; exit 0; }

HOOKS="$HOOKS" SETTINGS="$settings" HOOKS_DIR="$hooks_dir" python3 - <<'REGISTER_PY'
import json, os, shutil, sys

settings_path = os.environ["SETTINGS"]
hooks_dir = os.environ["HOOKS_DIR"]

try:
    with open(settings_path) as fh:
        data = json.load(fh)
except Exception as exc:  # noqa: BLE001
    print(f"register-claude-hooks: cannot parse {settings_path} ({exc}); leaving it alone")
    sys.exit(0)
if not isinstance(data, dict):
    print(f"register-claude-hooks: {settings_path} is not an object; leaving it alone")
    sys.exit(0)

rows = [
    line.split("|", 2)
    for line in os.environ["HOOKS"].strip().splitlines()
    if line.strip()
]

hooks = data.setdefault("hooks", {})
added, skipped_missing, already = [], [], []

for event, matcher, script in rows:
    path = os.path.join(hooks_dir, script)
    if not os.path.isfile(path):
        skipped_missing.append(script)
        continue
    groups = hooks.setdefault(event, [])
    # Already registered? Compare on the command string, which is what actually
    # runs — not on the matcher, so re-registering under a second matcher is
    # still caught as a duplicate.
    if any(
        h.get("command") == path
        for g in groups
        if isinstance(g, dict)
        for h in g.get("hooks", [])
        if isinstance(h, dict)
    ):
        already.append(script)
        continue
    entry = {"hooks": [{"type": "command", "command": path}]}
    if matcher:
        entry["matcher"] = matcher
    groups.append(entry)
    added.append(f"{event}/{matcher or '*'} -> {script}")

if not added:
    print(
        "register-claude-hooks: nothing to add "
        f"({len(already)} already registered"
        + (f", {len(skipped_missing)} script(s) absent here: {', '.join(skipped_missing)}" if skipped_missing else "")
        + ")"
    )
    sys.exit(0)

# Back up before the first write, then write atomically: a half-written
# settings.json is the one outcome worse than an unregistered hook.
backup = settings_path + ".before-hook-register"
shutil.copy2(settings_path, backup)
tmp = settings_path + ".tmp"
with open(tmp, "w") as fh:
    json.dump(data, fh, indent=2)
    fh.write("\n")
os.replace(tmp, settings_path)

for line in added:
    print(f"register-claude-hooks: registered {line}")
if skipped_missing:
    print(f"register-claude-hooks: script(s) absent on this machine, not registered: {', '.join(skipped_missing)}")
print(f"register-claude-hooks: previous settings.json saved as {backup}")
REGISTER_PY
