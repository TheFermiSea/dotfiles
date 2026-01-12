#!/bin/bash
# Smart Pane Position - Detect existing columns and position in rightmost

# Get current layout
LAYOUT=$(zellij action dump-layout 2>&1)

# Count how many "pane split_direction" entries exist (indicates columns)
COLUMN_COUNT=$(echo "$LAYOUT" | grep -c 'split_direction="vertical"')

# Check if there are multiple columns
if [ "$COLUMN_COUNT" -gt 1 ]; then
    # Multiple columns exist - we need to focus the rightmost pane first
    # Move focus to the right until we can't anymore
    for i in {1..10}; do
        # Try to move right, if it fails we're at the rightmost
        zellij action focus-next-pane 2>/dev/null || break
    done

    # Now create pane downward in the current (rightmost) column
    DIRECTION="down"
else
    # Single column - create new column to the right
    DIRECTION="right"
fi

# Output the direction for the calling script
echo "$DIRECTION"
