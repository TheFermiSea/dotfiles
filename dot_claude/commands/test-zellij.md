---
description: Test zellij pane creation with a simple command
---

Test the zellij pane workflow by:

1. Opening a new pane on the right side
2. Running a simple bash command that creates a test file in ~/var/
3. Auto-closing the pane after 2 seconds

Execute this command:
```bash
zellij run --direction right --close-on-exit --name "test-pane" -- bash -c 'echo "Test completed at $(date)" > ~/var/test-$(date +%s).txt && echo "File created: ~/var/test-$(date +%s).txt" && sleep 2'
```

Then report: "Zellij pane test completed. Check ~/var/ for test files."
