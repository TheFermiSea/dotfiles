# Global instructions

Applies to every Claude Code session on every machine, regardless of project.
Distributed by chezmoi from `TheFermiSea/dotfiles`. **Rewritten 2026-09-11**; the
previous version was ~8 months stale and contradicted several rules established
since.

**A project's own `CLAUDE.md` / `AGENTS.md` overrides this file.** This is the
floor, not the ceiling. If a repo has `AGENTS.md`, that is the canonical agent
policy for it.

## Edit these with chezmoi, not in place

This file, `~/.claude/agents/`, `~/.zshrc`, `~/.ssh/config` and friends are
chezmoi-managed. Editing `~/.claude/CLAUDE.md` directly will be silently reverted
on the next `chezmoi apply`.

```bash
chezmoi edit ~/.claude/CLAUDE.md   # edit the source
chezmoi diff                       # what would change on this machine
chezmoi apply                      # apply
chezmoi re-add <file>              # local file is newer -> push it back to the repo
```

`autoCommit` and `autoPush` are on, so a `chezmoi edit`/`re-add` commits and
pushes by itself. **Never put a live credential in a managed file** — rotating
tokens (`.codex/auth.json`, `.gemini/oauth_creds.json`) are in `.chezmoiignore`
for exactly that reason, and secrets belong in `~/.zshrc.secrets`, which is
age-encrypted in the repo.

## Search: pick the right tool, and prove a zero before reporting it

| Question | Tool |
|----------|------|
| "What code has this *shape*?" (calls, impls, signatures) | `ast-grep` |
| "Where does this *exact text* appear?" (an id, an error string, a log line) | `rg` |
| "What code *does* this thing?" (by concept) | `ccc search`, where indexed |

The binary is **`ast-grep`** (0.45.1). The old `sg` alias still runs but prints a
deprecation warning — use `ast-grep`.

**ALWAYS run a positive control before believing an absence.** Run the same
pattern against something you know contains the thing; if it returns zero there
too, the pattern is wrong, not the code. A pattern-form mistake and a genuine
absence look identical in the output. Three ways `ast-grep` under-reports:

- **Bare call vs method call are different AST nodes.** `foo($$$)` will NOT match
  `x.foo(...)`. Use `$P.foo($$$)`.
- **Macro bodies are opaque** — tree-sitter parses a `macro_rules!` body as a
  token tree. Fall back to `rg -c 'the_macro!\('`.
- **Fully-qualified trait paths**: `impl Foo for T` does not match
  `impl a::b::Foo for T`.

**A search that returns nothing is evidence about the search.** Before reporting
that something does not exist, state what your search *could* have matched and
confirm the thing would have been inside that set. Positive findings validate
themselves; negative ones are equally consistent with the tool never having run.

Prefer `rg` / `fd` / `ast-grep` over shell `grep`/`find` pipelines.

## Verification: three checks answer three different questions

- **Review** answers *"do these two sites agree?"* — no run can see that.
- **Execution** answers *"is this path actually reached?"* — no reading can see
  that. Reading forward through a path tells you what it *would* do, never
  whether anything enters it. **Never assert a causal chain you have not run.**
- **Falsification** answers *"can this assertion distinguish?"* — confirm every
  new test FAILS with its fix reverted. A test can run the right path and still
  be blind, e.g. a missing-sign fix covered by a fixture of `0.0`, a fixed point
  of the operation.

**A green suite is evidence only about the input shapes the tests instantiate.**
Enumerate the production shapes no test covers before concluding a path works.

## Shell

- **Never pass prose through shell quoting.** No `git commit -m "…"` /
  `--body "…"` for text containing a backtick, `$(`, `${` or `$VAR` — the shell
  executes those first. Use `git commit -F <file>`, `--body-file <file>`, or a
  heredoc with a **quoted, unique** delimiter (`<<'MSG_x7'`).
- **`ls` is aliased to `eza`.** `ls -t` errors instead of sorting by time; use
  `/bin/ls` when you need POSIX flags.
- **`timeout` does not exist on macOS.** Use `gtimeout` (coreutils) or omit it.
  Silent exit 127 is the tell.
- Quote paths that may contain spaces; prefer `"$var"` everywhere.

## Issue tracking and memory

**Where a project has `.beads/`, `bd` is the tracker.** Not TodoWrite, not
markdown TODO lists, not a parallel file.

```bash
bd ready                                # available unblocked work
bd show <id>  /  bd update <id> --claim
bd close <id> --reason "<what landed>"  # --reason is REQUIRED
bd children <epic>                      # NEVER count children by dotted ID prefix
```

- **Never hand-roll SQL against the beads/Dolt tables.** bd ships `stale`,
  `lint`, `find-duplicates`, `blocked`, `ready`, `children`, `epic status`,
  `epic close-eligible`, `supersede`, `graph`, `prune`, `purge`, and a formula /
  molecule / wisp workflow system. Querying around it manufactures bugs.
- **`bd remember` is the durable memory**, not MEMORY.md or progress files.
- `bd dep cycles` walks only the blocking graph and cannot see parent-child
  cycles. Native canary: time `bd list --all` (healthy is seconds).

Where a project has no `.beads/`, the per-project memory directory under
`~/.claude/projects/<slug>/memory/` is the fallback. **ByteRover (`brv`) is
removed as of 2026-09-11 — do not reinstall or reference it.**

## Toolchains

`mise` manages per-project tool versions. A repo with `.mise.toml` needs
`mise trust` once per machine — an untrusted config surfaces as a **parse error**,
which is misleading. `mise install` then gets the pinned versions.

Tool drift between machines is not cosmetic: `jq` missing on one box silently
disabled every Bash guardrail in a repo's hooks, because the dispatcher read its
input through `jq` and exited 0 without a word.

## Git

- Feature branch + PR. Do not push directly to `main`.
- Conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`.
- **Re-read the full diff before pushing.** If a reviewer would ask "why is this
  file here?", it does not belong in the push.
- **Preserve unlanded work.** During any cleanup, the default is KEEP — branches
  with unmerged commits, stashes, untested work. Deleting is the user's call, not
  a tidiness decision.
- **Copilot review is billed** and auto-fires per PR opened and per follow-up
  push. Batch changes; request it deliberately on substantial PRs only.

## Never

- **Never reintroduce an LLM account-pooling or credential-forwarding proxy.**
  VibeProxy, CLIProxyAPI/CLIProxyPlus, LLM-API-Key-Proxy and similar were removed
  2026-09-10 and 2026-09-11. If one tool needs an OpenAI-compatible endpoint, set
  its base URL for that tool alone — never globally, never in `/etc`, never in a
  shell rc.
- Never create documentation files proactively unless asked.
- Never save working files to a project root; use a scratch dir.
- Never proceed on an architectural decision under real uncertainty — ask.

## When stuck

1. Simplify to a minimal case.
2. Isolate — one failing test, not the suite.
3. Check recent commits; a break usually has a cause in the last few.
4. Ask rather than guess, when different readings would mean materially different
   work.
5. Checkpoint: commit the working state and record the blocker in `bd`.

## Per-machine facts

Machines are on a Tailscale tailnet. `ssh <name>` works for the Linux boxes.

| Host | Role |
|------|------|
| `brians-macbook-pro-2310` | primary laptop |
| `ai-proxy` | main Linux dev box, runs the shared Dolt server for beads |
| `leabs-dev` | Andor SDK3 / echelle host |
| `maitai-eos` | hardware rig (`maitai@maitai-eos`), PVCAM SDK at `/opt/pvcam/sdk` |
| `ceng-gh62pk3` | Windows box — Class-IV laser, Ghidra, Solis |
| `cocoindex-server` | TEI embedding server for `ccc` |

Rig-specific hardware detail belongs in the project repo, not here.
