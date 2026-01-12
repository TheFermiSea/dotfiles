---
description: Delegate a task to a sub-agent with live monitoring in a zellij pane
argument-hint: <task-description>
---

Delegate the following task to a sub-agent: **$ARGUMENTS**

Execute this complete workflow:

## Step 1: Prepare Task Environment

Generate task identifiers:
```bash
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
# Cross-platform: use md5 on macOS, md5sum on Linux
if command -v md5 &>/dev/null; then
    TASK_HASH=$(echo "$ARGUMENTS" | md5 | cut -c1-8)
else
    TASK_HASH=$(echo "$ARGUMENTS" | md5sum | cut -c1-8)
fi
RESULT_FILE="$HOME/var/claude-agent-results/task-${TIMESTAMP}-${TASK_HASH}.md"
mkdir -p "$HOME/var/claude-agent-results"
```

## Step 2: Launch Monitoring Pane (Smart Positioning)

Determine the correct direction for pane placement:

```bash
# Smart positioning logic:
# - 1 column: Create new pane RIGHT (creates new rightmost column)
# - Multiple columns: Navigate to TOP of rightmost column, create DOWN

# Count columns by checking layout
LAYOUT=$(zellij action dump-layout 2>&1)
# Count panes with split_direction="vertical" in the active tab
# Filter for the focused tab section only
COLUMN_COUNT=$(echo "$LAYOUT" | awk '/focus=true hide_floating_panes=true/,/^    \}/' | grep -c 'split_direction="vertical"')

if [ "$COLUMN_COUNT" -eq 0 ]; then
    # Single column layout - create new column to the right
    DIRECTION="right"
else
    # Multiple columns - navigate to rightmost column only (don't move up/down)
    # Then create down - this will stack vertically in that column
    # Move to rightmost column
    for i in {1..10}; do
        zellij action move-focus right 2>/dev/null || break
    done

    # Create pane down from current position in rightmost column
    # Agent panes will stack vertically from wherever focus is
    DIRECTION="down"
fi

# Launch with close-on-exit flag so it auto-closes when script finishes
zellij action new-pane --close-on-exit --direction "$DIRECTION" --name "sub-agent-${TASK_HASH}" -- ~/.claude/commands/scripts/spawn-agent-pane.sh "$ARGUMENTS" "$RESULT_FILE"
```

The pane will:
- Position intelligently (down if rightmost column exists, right if not)
- Stack vertically with other agent panes in same column
- Display task information with visual header
- Show progress updates every 5 seconds
- Monitor for result file creation
- Auto-close 3 seconds after completion
- Stay open for entire task duration (max 5 minutes)
- Close automatically when script exits (--close-on-exit)

## Step 3: Spawn Sub-Agent (Immediately After Pane Launch)

Use Task tool with subagent_type="general-purpose" with this prompt:

```
Task: $ARGUMENTS

Instructions:
1. Execute the task: "$ARGUMENTS"
2. Gather all necessary information using available tools
3. Create a comprehensive markdown report with your findings
4. Write the complete results to: $RESULT_FILE

Format the output file as:
---
task_id: ${TIMESTAMP}-${TASK_HASH}
task: $ARGUMENTS
timestamp: $(date '+%Y-%m-%d %H:%M:%S')
status: completed
---

# Task Results: $ARGUMENTS

## Summary
[Executive summary of findings]

## Detailed Results
[Main content organized in clear sections]

## Conclusions
[Key takeaways and recommendations]

## Metadata
- Completion time: [timestamp]
- Tools used: [list of tools]

CRITICAL: Ensure you write the complete results to $RESULT_FILE before finishing.
The monitoring pane is waiting for this file to contain content.

Return message: "Task '$ARGUMENTS' completed. Results written to: $RESULT_FILE"
```

## Step 4: Notification

After sub-agent completes, notify me:
"✅ Sub-agent task completed: '$ARGUMENTS'

📄 Results available at: $RESULT_FILE
🖥️  Monitoring pane will close after user acknowledges (press any key in pane)"

## Expected Behavior

1. **Pane appears** at top of rightmost column
2. **Shows live status** - updates every 5 seconds while waiting
3. **Stays open** during entire task execution
4. **Shows completion** when result file is created
5. **Waits for user** to press a key before closing
6. **Parent agent notified** with result file path

Execute all steps in sequence now.
