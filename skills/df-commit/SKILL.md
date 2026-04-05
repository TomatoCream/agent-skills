---
name: df-commit
description: Use when you need to commit changes and push them to a remote repository - guides sensible commit creation with review before committing
---

# Sensible Committing

## Overview

Commit changes with intentional messages and push to remote.

**Core principle:** Review diff → Craft message → Commit → Push.

## The Process

### Step 1: Review Changes

```bash
git status
git diff --staged
```

Check what will be committed.

### Step 2: Review Unstaged Changes

```bash
git diff
```

Understand full scope of changes.

### Step 3: Craft Commit Message

Write a message that explains **why** not just **what**:

```
<type>: short summary (50 chars max)

Detailed explanation if needed. What problem does this solve?
Why was this change necessary?

Refs: #<issue-number> (if applicable)
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### Step 4: Commit

```bash
git add <paths> && git commit -m "<message>"
```

### Step 5: Push

```bash
git push
```

If branch is new:
```bash
git push -u origin $(git branch --show-current)
```

## Quick Reference

| Step | Command | Purpose |
|------|---------|---------|
| Review staged | `git diff --staged` | See what will commit |
| Review all | `git diff` | See unstaged changes |
| Stage files | `git add <paths>` | Choose what to commit |
| Commit | `git commit -m "<msg>"` | Create commit |
| Push | `git push` | Send to remote |

## Common Mistakes

**Empty commit messages**
- Problem: Unclear history, can't generate changelog
- Fix: Require meaningful message before proceeding

**Committing everything blindly**
- Problem: Mixed concerns, unrelated changes
- Fix: Review each diff before staging

**No push after commit**
- Problem: Changes only local
- Fix: Push immediately after commit

## Red Flags

**Stop if:**
- No files staged
- Commit message is vague ("fix stuff", "updates")
- Pushing to wrong remote
