Run a security audit on Rust code using AST-grep.

Execute these searches and report findings:

1. **Unsafe blocks**: `sg -p 'unsafe { $$$ }' --lang rust`
2. **Unwrap calls**: `sg -p '$EXPR.unwrap()' --lang rust`
3. **Expect calls**: `sg -p '$EXPR.expect($MSG)' --lang rust`
4. **Panic macro**: `sg -p 'panic!($$$)' --lang rust`

For each category:
- Report the count
- Show the first 5 matches with file:line
- Suggest improvements for critical findings

$ARGUMENTS
