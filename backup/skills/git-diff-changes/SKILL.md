---
name: git-diff-changes
description: >
  Collect the git diff of changes on the current branch compared to origin/master or origin/main.
  Use this skill whenever you need to gather what code was changed before feeding it into another
  skill or prompt — for instance, before a code review, generating a merge request description,
  summarizing changes, or any task that asks "what did we change?". By default, test files are
  excluded (Java repos: *Test.java, *Tests.java, *IT.java, src/test/**, etc.) so the diff focuses
  on production code. Include test files only when the task is explicitly about reviewing or
  analyzing tests. Trigger on: "get the diff", "what changed", "show changes", "collect changes",
  "review my changes", "diff against main", "diff against master", or whenever another skill
  needs the set of changes as input.
---

# Git Diff Changes

Collect the diff of changes on the current branch for use by other skills or prompts.

## How it works

1. **Detect the base branch** — check which remote branch exists as the merge target:
   - If the user provides a specific branch or ref, use that.
   - Otherwise, auto-detect: try `origin/master`, then `origin/main`, then fall back to `HEAD~1`.
   - Use `git merge-base` to find the common ancestor so the diff is clean.

2. **Generate the diff** with test files excluded by default:
   ```bash
   # Find the merge base
   BASE=$(git merge-base HEAD <target-branch>)

   # Diff excluding test files (default)
   git diff $BASE...HEAD \
     -- . \
     ':!src/test/' \
     ':!**/src/test/' \
     ':!**/*Test.java' \
     ':!**/*Tests.java' \
     ':!**/*IT.java' \
     ':!**/*Spec.java' \
     ':!**/*TestCase.java' \
     ':!**/test/**'
   ```

3. **Also list changed files** so downstream consumers can see the scope at a glance:
   ```bash
   git diff --name-only $BASE...HEAD \
     -- . \
     ':!src/test/' \
     ':!**/src/test/' \
     ':!**/*Test.java' \
     ':!**/*Tests.java' \
     ':!**/*IT.java' \
     ':!**/*Spec.java' \
     ':!**/*TestCase.java' \
     ':!**/test/**'
   ```

## When to include test files

Only include test files when the user's task is specifically about tests. Examples:
- "review my unit tests"
- "check the test changes"
- "review test coverage"

In that case, run the diff **without** the exclusion pathspecs — or if you want only test files, invert the filter:
```bash
git diff $BASE...HEAD \
  -- 'src/test/' '**/src/test/' '**/*Test.java' '**/*Tests.java' '**/*IT.java'
```

## Handling edge cases

- **Uncommitted changes**: If there are unstaged or staged changes that haven't been committed yet, include them by appending the working tree diff. Tell the user you're including uncommitted changes.
- **No remote**: If `origin/master` and `origin/main` don't exist (e.g., fresh repo), fall back to diffing against `HEAD~1` or the initial commit.
- **Large diffs**: If the diff is very large (>3000 lines), mention this to the user and consider summarizing the file list first, then showing diff per file as needed by the downstream task.
- **Binary files**: Skip binary files in the diff output — they're noise for downstream consumers.

## Output

Present the results clearly so they can be consumed by the next step:

1. **Summary line**: "N files changed against `<base-ref>`" (with or without test files noted)
2. **File list**: the `--name-only` output
3. **Full diff**: the complete diff content

The downstream skill or prompt receives all three pieces. If the diff is being piped into a review skill, the file list helps it prioritize, and the full diff provides the detail.
