# Global AI Agent Guidelines

This file provides guidelines for AI agents working across all projects for user: **squires.b@gmail.com**

## Primary Coordination System: Beads

Use **beads (`bd`)** for task coordination and progress tracking when a project uses it.

### Standard Workflow

```bash
# 1) Check unblocked work
bd ready --json

# 2) Claim task
bd update <issue-id> --status in_progress --json

# 3) Work - code, test, verify
# ... your work here ...

# 4) Record findings in issue updates/comments as needed
bd show <issue-id> --json

# 5) Complete task
bd close <issue-id> --reason "Done" --json
```

### Best Practices

Always:
- Use issue IDs in commits, notes, and status updates when available (for example `bd-123`)
- Keep issue status accurate (`open`, `in_progress`, `blocked`, `closed`)
- Add concrete technical notes with file references when useful
- Run project quality checks before finalizing changes

Never:
- Leave claimed issues stale without status updates
- Close issues without confirming implementation and validation
- Add vague progress notes that lack technical detail

## Multi-Agent Coordination

When multiple agents work in the same repo:
1. Retrieve current work from `bd ready` / `bd list`
2. Claim work before editing
3. Update status promptly when blocked or complete
4. Cross-reference related issues and dependencies

## Project Standards

### Issue Tracking

Projects may use different systems:
- **beads (`bd`)**: preferred when configured
- **GitHub Issues**
- **Linear/Jira**

Use the project’s configured system and reference IDs in your notes.

### Code Quality

Use project-native tooling:
- Rust: `clippy`, `rustfmt`
- TypeScript: `eslint`, `prettier`, `tsc`
- Python: `ruff`, `black`, `mypy`

### Testing

- Run relevant unit/integration/e2e tests before finishing
- Prefer targeted tests for changed areas plus project-required full checks

### Documentation

Keep docs current when behavior or architecture changes:
- README/setup docs
- architecture/design notes
- changelog/release notes when used

## Code Search

### ColGrep — Semantic Code Search

Use `colgrep` for semantic/conceptual code search. It uses multi-vector embeddings (LateOn-Code 130M, ColBERT) for high-accuracy retrieval.

```bash
# Semantic search (find by meaning)
colgrep "database connection pooling"

# Hybrid: regex filter + semantic ranking
colgrep -e "async fn" "error handling with retry"

# Scoped to file type
colgrep --include="*.rs" "frame streaming"

# JSON output for programmatic use
colgrep --json "authentication"
```

**When to use colgrep vs grep/rg:**
- `colgrep`: Conceptual queries, exploring unfamiliar code, finding by intent
- `grep`/`rg`: Exact string matches, specific identifiers, known patterns

ColGrep auto-indexes on first use. For manual refresh: `colgrep init .`

## Security and Privacy

Never commit:
- API keys, tokens, or credentials
- Personal or private data

Always:
- Use environment variables for secrets
- Review diffs for sensitive data before pushing
- Follow project security practices

## Communication

With users:
- Ask for clarification when requirements are ambiguous
- Report blockers quickly
- Keep updates concise and technical

With other agents:
- Coordinate through the project issue tracker and code comments

## Success Criteria

An effective agent:
- Claims and updates work clearly
- Produces tested, working code
- Documents key technical decisions
- Leaves issue tracker state accurate


<!-- BEGIN BEADS INTEGRATION -->
## Issue Tracking with bd (beads)

**IMPORTANT**: This project uses **bd (beads)** for ALL issue tracking. Do NOT use markdown TODOs, task lists, or other tracking methods.

### Why bd?

- Dependency-aware: Track blockers and relationships between issues
- Git-friendly: Auto-syncs to JSONL for version control
- Agent-optimized: JSON output, ready work detection, discovered-from links
- Prevents duplicate tracking systems and confusion

### Quick Start

**Check for ready work:**

```bash
bd ready --json
```

**Create new issues:**

```bash
bd create "Issue title" --description="Detailed context" -t bug|feature|task -p 0-4 --json
bd create "Issue title" --description="What this issue is about" -p 1 --deps discovered-from:bd-123 --json
```

**Claim and update:**

```bash
bd update bd-42 --status in_progress --json
bd update bd-42 --priority 1 --json
```

**Complete work:**

```bash
bd close bd-42 --reason "Completed" --json
```

### Issue Types

- `bug` - Something broken
- `feature` - New functionality
- `task` - Work item (tests, docs, refactoring)
- `epic` - Large feature with subtasks
- `chore` - Maintenance (dependencies, tooling)

### Priorities

- `0` - Critical (security, data loss, broken builds)
- `1` - High (major features, important bugs)
- `2` - Medium (default, nice-to-have)
- `3` - Low (polish, optimization)
- `4` - Backlog (future ideas)

### Workflow for AI Agents

1. **Check ready work**: `bd ready` shows unblocked issues
2. **Claim your task**: `bd update <id> --status in_progress`
3. **Work on it**: Implement, test, document
4. **Discover new work?** Create linked issue:
   - `bd create "Found bug" --description="Details about what was found" -p 1 --deps discovered-from:<parent-id>`
5. **Complete**: `bd close <id> --reason "Done"`

### Auto-Sync

bd automatically syncs with git:

- Exports to `.beads/issues.jsonl` after changes (5s debounce)
- Imports from JSONL when newer (e.g., after `git pull`)
- No manual export/import needed!

### Important Rules

- ✅ Use bd for ALL task tracking
- ✅ Always use `--json` flag for programmatic use
- ✅ Link discovered work with `discovered-from` dependencies
- ✅ Check `bd ready` before asking "what should I work on?"
- ❌ Do NOT create markdown TODO lists
- ❌ Do NOT use external issue trackers
- ❌ Do NOT duplicate tracking systems

For more details, see README.md and docs/QUICKSTART.md.

<!-- END BEADS INTEGRATION -->
