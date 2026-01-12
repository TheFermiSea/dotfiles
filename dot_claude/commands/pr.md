Create a pull request for the current branch.

1. Check current branch is not main/master
2. Run `git status` to see uncommitted changes
3. If there are uncommitted changes, ask if I should commit them first
4. Push the current branch with `git push -u origin HEAD`
5. Create PR using `gh pr create --fill` (or with custom title/body if provided)
6. Report the PR URL

$ARGUMENTS
