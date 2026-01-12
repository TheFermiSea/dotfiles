Run comprehensive Python quality checks on the current project.

Execute these commands in sequence:

1. `ruff check .` - Run linter
2. `ruff format --check .` - Check formatting
3. `pytest` - Run tests (if pytest is available)

If any check fails, suggest the fix. If all pass, report success.

$ARGUMENTS
