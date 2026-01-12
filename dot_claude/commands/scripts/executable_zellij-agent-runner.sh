#!/bin/bash
# Zellij Agent Runner Script
# This script runs in a zellij pane, executes a sub-agent task, and saves results

# Generate unique task identifier
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
TASK_ID=$(echo "$1" | md5sum | cut -c1-8)
RESULT_FILE="$HOME/var/task-${TIMESTAMP}-${TASK_ID}.md"

# Ensure var directory exists
mkdir -p "$HOME/var"

# Create initial results file with task info
cat > "$RESULT_FILE" << EOF
# Sub-Agent Task Results

**Task ID**: ${TASK_ID}
**Timestamp**: ${TIMESTAMP}
**Task Description**: $*

---

## Task Execution

EOF

# Note: Claude Code doesn't have a direct CLI interface to spawn agents
# Instead, we'll document the task and let the parent agent handle it
# In a real implementation, this would interface with Claude Code's agent system

echo "## Agent Output" >> "$RESULT_FILE"
echo "" >> "$RESULT_FILE"
echo "Task: $*" >> "$RESULT_FILE"
echo "" >> "$RESULT_FILE"
echo "Status: Ready for agent execution" >> "$RESULT_FILE"
echo "" >> "$RESULT_FILE"
echo "_Note: This task was delegated via zellij pane. Parent agent should use Task tool to execute._" >> "$RESULT_FILE"

# Output the result file path (this will be visible in the pane)
echo "═══════════════════════════════════════════════════"
echo "Task prepared for sub-agent execution"
echo "Result file: $RESULT_FILE"
echo "═══════════════════════════════════════════════════"

# Keep pane open briefly so user can see the output
sleep 2
