Run comprehensive Rust quality checks on the current project.

Execute these commands in sequence, stopping if any fail:

1. `cargo fmt --all -- --check` - Check formatting
2. `cargo clippy --all-targets -- -D warnings` - Run linter
3. `cargo test` - Run tests

If any check fails, suggest the fix. If all pass, report success.

$ARGUMENTS
