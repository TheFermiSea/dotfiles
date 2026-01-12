---
description: Start a Ralph loop with beads issue tracking, planning mode, and harness patterns
argument-hint: "[--mode plan|build] [--issue <id>] [--priority 1-4] [--max-iterations N] [--dry-run] <task>"
---

Start a Ralph loop with beads issue tracking and Anthropic-recommended harness patterns.

This command implements the Ralph Playbook methodology with two modes:
- **PLANNING**: Gap analysis, task decomposition, creates IMPLEMENTATION_PLAN.md
- **BUILDING**: Execute tasks from plan, one per iteration, with validation gates

## Arguments

Parse the following from $ARGUMENTS:
- `--mode <plan|build>` - Execution mode (default: build)
- `--issue <id>` - Resume existing beads issue (skip creation)
- `--priority <1-4>` - Issue priority (default: 2)
- `--max-iterations <n>` - Maximum iterations before stopping (default: 20 for build, 5 for plan)
- `--dry-run` - Preview setup without executing Ralph
- Everything else is the task description

**CRITICAL:** A completion promise is ALWAYS required:
- PLANNING mode: `PLAN_READY`
- BUILDING mode: `DONE`

## Setup Phase

### Step 1: Determine Mode

**If `--mode plan` specified:**
- Set mode to PLANNING
- Default max-iterations to 5 (planning is faster)
- Completion promise: `PLAN_READY`

**If `--mode build` or no mode specified:**
- Set mode to BUILDING
- Default max-iterations to 20
- Completion promise: `DONE`

### Step 2: Issue Management

**If `--issue <id>` provided (resume mode):**
Run: `bd show <id>` to verify issue exists and check for blockers, then `bd update <id> --status in_progress`.
Use the provided issue ID. Check the notes for previous iteration count to continue numbering.
If the issue shows blockers (depends on other issues), report them before proceeding.

**Otherwise (new issue):**

First, detect issue type from task description keywords:
- Contains "fix", "bug", "error", "crash" → type=bug
- Contains "feat", "add", "implement", "create" → type=feature
- Contains "refactor", "clean", "improve" → type=task
- Contains "test", "coverage" → type=task
- Default → type=task

Run: `bd create --title="Ralph: <task-summary>" --type=<detected-type> --priority=<priority>`

Then add labels for filtering:
Run: `bd label add <issue-id> ralph` and `bd label add <issue-id> automated`

Note the generated issue ID (e.g., project-abc123).

### Step 3: Record Start Time

Note the current time for duration tracking: `date +%s` (Unix timestamp)

### Step 4: Auto-Detect Test Framework

Check which test framework exists by looking for project files:
- If `Cargo.toml` exists → Rust project, use `cargo nextest run` or `cargo test`
- If `pyproject.toml`, `setup.py`, or `tests/` exists → Python project, use `pytest`
- If `package.json` exists → Node project, use `npm test`

Store detected framework for use in completion criteria.

### Step 5: Initialize Plan File

Check if `.claude/IMPLEMENTATION_PLAN.md` exists.

**If it does NOT exist:**
Create it with initial structure:
```markdown
# Implementation Plan

## Status
- Mode: <PLANNING|BUILDING>
- Issue: <issue-id>
- Created: <timestamp>

## Objective
<task description>

## Tasks
<!-- Ralph will populate during planning phase -->

## Learnings
<!-- Operational notes discovered during execution -->
```

**If it exists:**
- In PLANNING mode: It will be regenerated/updated
- In BUILDING mode: Read current state to continue

### Step 6: Dry-Run Check

**If `--dry-run` specified:**
- Display: Mode, Issue ID, priority, type, labels, detected test framework, plan file status, task description
- Output: "DRY RUN COMPLETE - no Ralph loop started"
- Exit without invoking Ralph

## Start Ralph Loop

**MANDATORY:** Use the Skill tool to invoke `ralph-loop:ralph-loop` with these arguments:

    --completion-promise '<promise>' --max-iterations <N> <prompt>

Where:
- `--completion-promise` - `'PLAN_READY'` for planning mode, `'DONE'` for building mode
- `--max-iterations <N>` - use value from $ARGUMENTS or defaults (5 for plan, 20 for build)
- `<prompt>` - the mode-specific structured prompt below with all placeholders filled in

---

## PLANNING MODE PROMPT

Use this prompt when mode is PLANNING:

---BEGIN PLANNING PROMPT---
PLANNING MODE: <task description>. Beads issue: <issue-id>. Start time: <unix-timestamp>.

## Your Role

You are in PLANNING mode. Your ONLY job is to:
1. Study the codebase and requirements
2. Perform gap analysis (what exists vs what's needed)
3. Create/update IMPLEMENTATION_PLAN.md with prioritized tasks
4. Do NOT implement any code
5. Do NOT make any commits

## Startup Ritual (MANDATORY - EVERY iteration)

Before doing ANY work, complete ALL of these steps:

1. **Read progress state:** Run `bd show <issue-id>`. Parse the notes to find the last iteration number. If resuming, continue from that number.

2. **Study existing code:** Use the Task tool with `Explore` agent to understand the codebase architecture. DON'T ASSUME NOT IMPLEMENTED - verify what actually exists before planning new work. Look for existing patterns, utilities, and conventions.

3. **Read current plan:** If `.claude/IMPLEMENTATION_PLAN.md` exists, read it to understand previous planning progress.

## Planning Protocol

Using parallel subagents (Task tool with Explore agent), investigate:
- Current codebase structure relevant to the task
- Existing implementations that relate to the goal
- Test coverage and patterns
- Dependencies and integration points

Then perform gap analysis:
- What functionality exists?
- What is missing?
- What needs modification?

## Update Implementation Plan

Write/update `.claude/IMPLEMENTATION_PLAN.md` with this structure:

```markdown
# Implementation Plan

## Status
- Mode: PLANNING → READY FOR BUILD
- Issue: <issue-id>
- Last Updated: <timestamp>
- Planning Iterations: <N>

## Objective
<clear description of the goal>

## Gap Analysis
### What Exists
- <existing functionality>

### What's Missing
- <gaps identified>

### What Needs Modification
- <changes to existing code>

## Tasks (Prioritized)

### Task 1: <title>
- **Priority:** P1 (do first)
- **Files:** <files to create/modify>
- **Acceptance Criteria:**
  - [ ] <observable outcome 1>
  - [ ] <observable outcome 2>
- **Tests Required:**
  - [ ] <test description>

### Task 2: <title>
...

## Learnings
<!-- Operational notes for building phase -->
- Build command: <command>
- Test command: <command>
- Key patterns: <patterns discovered>
```

## MANDATORY: Structured Progress Notes

At the END of EVERY iteration, run: `bd update <issue-id> --notes "[plan:N] [tasks:T] [gaps:G] <summary>"`

Where: N = planning iteration, T = tasks defined, G = gaps identified

## Completion Criteria

Output <promise>PLAN_READY</promise> ONLY when:
- Gap analysis is complete
- All tasks are defined with acceptance criteria
- Tasks are prioritized
- Test requirements are specified
- Plan is ready for BUILDING mode

Do NOT output the promise if the plan is incomplete or unclear.

## On Completion

Run: `bd update <issue-id> --notes "[PLAN COMPLETE] <T> tasks defined, ready for: /ralph-tracked --mode build --issue <issue-id>"`
---END PLANNING PROMPT---

---

## BUILDING MODE PROMPT

Use this prompt when mode is BUILDING:

---BEGIN BUILDING PROMPT---
BUILDING MODE: <task description>. Beads issue: <issue-id>. Start time: <unix-timestamp>. Test framework: <detected-framework or "none">.

## Your Role

You are in BUILDING mode. Follow the implementation plan and execute ONE task per iteration.

## Startup Ritual (MANDATORY - EVERY iteration)

Before doing ANY work, complete ALL of these steps:

1. **Read progress state:** Run `bd show <issue-id>`. Parse the notes to find the last iteration number. If resuming, continue from that number. Check if any blockers are listed.

2. **Check git state:** Run `git status` and `git log -3 --oneline`. Note the current commit count for this session.

3. **Read implementation plan:** Read `.claude/IMPLEMENTATION_PLAN.md` to understand:
   - Which tasks are complete (checked off)
   - Which task is next (highest priority unchecked)
   - Acceptance criteria for that task
   - Required tests

4. **Study existing code:** Before implementing, use Task tool with Explore agent to study relevant existing code. DON'T ASSUME NOT IMPLEMENTED - verify what exists. Look for patterns to follow.

5. **Run baseline tests (if framework detected):** Run the detected test command. Record: tests passed, failed, skipped counts. If tests fail, fix them BEFORE proceeding with new work.

## Subagent Strategy

**CRITICAL for context management:**
- Use Task tool with `Explore` agent for codebase searches (keeps main context clean)
- Use parallel subagents for independent file reads
- Use SINGLE agent for running tests/build - this provides sequential validation gates
- Never run tests in parallel - they must provide backpressure

## Work Protocol

- Focus on ONE specific task from the plan per iteration
- Make incremental progress, not wholesale changes
- Follow existing patterns discovered during exploration
- Commit after each meaningful change with message format: `<type>(<scope>): <description> (<issue-id>)`

After completing a task:
- Update `.claude/IMPLEMENTATION_PLAN.md` to check off completed items
- Add any learnings to the Learnings section
- Run tests to verify (SINGLE agent, not parallel)

## MANDATORY: Structured Progress Notes

At the END of EVERY iteration, run: `bd update <issue-id> --notes "[iter:N] [tests:P/F/S] [commits:M] [files:K] [task:T/Total] <summary>"`

Where: N = iteration number, P/F/S = tests passed/failed/skipped, M = commits this iteration, K = files changed, T/Total = task number completed / total tasks

Example: `[iter:3] [tests:42/0/2] [commits:2] [files:4] [task:2/5] Completed validation logic`

## Completion Criteria

**To exit the loop**, output <promise>DONE</promise> ONLY when ALL conditions are met:
- All tasks in IMPLEMENTATION_PLAN.md are checked complete
- Tests pass (run detected test framework)
- Git status is clean (all changes committed)
- Code is ready to merge

**IMPORTANT:** The <promise>DONE</promise> tag is the ONLY way to exit the loop gracefully. Do NOT output it unless the conditions above are genuinely satisfied.

## On Completion

1. Calculate metrics: Run `END_TIME=$(date +%s)` then `DURATION=$((END_TIME - <start-timestamp>))` then `MINUTES=$((DURATION / 60))`. Also gather: Total iterations from notes, Final test counts, Total commits made (from git log), Total files changed (from git diff --stat against starting commit).

2. Close with structured summary: Run `bd close <issue-id> --reason "Completed in ${MINUTES}m | ${ITERATIONS} iterations | ${TESTS_PASSED} tests passing | ${COMMITS} commits | ${FILES} files changed | Summary: <what was accomplished>"`

## If Max Iterations Reached

- Do NOT close the beads issue
- Update with detailed blockers: Run `bd update <issue-id> --notes "[BLOCKED after N iterations] [task:T/Total] Attempted: <what was tried>. Blockers: <specific issues>. Next: /ralph-tracked --issue <issue-id> --max-iterations 40"`
- The issue remains open for manual review or resume
---END BUILDING PROMPT---

---

## Resume Instructions

**To resume planning:**
```
/ralph-tracked --mode plan --issue <issue-id> "<continue planning>"
```

**To resume building:**
```
/ralph-tracked --mode build --issue <issue-id> "<continue building>"
```

**To switch from planning to building:**
```
/ralph-tracked --mode build --issue <issue-id> "Execute the implementation plan"
```

The startup ritual will:
1. Parse previous iteration count from notes
2. Read existing IMPLEMENTATION_PLAN.md
3. Check for any blockers
4. Continue from where it left off

## Typical Workflow

1. **Start with planning:**
   ```
   /ralph-tracked --mode plan "Add feature X to the system"
   ```

2. **Switch to building when plan is ready:**
   ```
   /ralph-tracked --mode build --issue <issue-id> "Execute the plan"
   ```

3. **Resume if interrupted:**
   ```
   /ralph-tracked --issue <issue-id> "Continue work"
   ```

$ARGUMENTS
