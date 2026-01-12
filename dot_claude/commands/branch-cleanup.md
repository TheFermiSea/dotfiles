Clean up local git branches that have been merged or deleted on remote.

1. Fetch and prune remote branches: `git fetch --prune`
2. List branches marked as [gone]: `git branch -vv | grep ': gone]'`
3. Show what would be deleted and ask for confirmation
4. If confirmed, delete the stale local branches
5. Report how many branches were cleaned up

$ARGUMENTS
