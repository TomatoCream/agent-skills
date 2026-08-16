---
name: df-think-say-approve-do
description: >
  Enforce a strict think → describe → approve → execute loop before taking any action.
  Use this skill when the user invokes /df-think-say-approve-do, or whenever they say
  things like "plan before acting", "show me what you'll do first", "don't do anything
  without asking", "walk me through before you run it", or "think out loud before
  executing". Also trigger proactively when the task involves irreversible or risky
  operations (deleting files, running migrations, pushing code, bulk edits) and the
  user hasn't explicitly pre-authorized each step.
---

# Think → Say → Approve → Do

This skill enforces a deliberate pause before executing anything. The goal is to keep
the user fully in control: they see the full plan, approve it, and only then does
execution happen.

## The four phases

### 1. Think

Before writing a single tool call or shell command, reason through the task:

- What is the end goal?
- What is the minimal sequence of steps to get there?
- What could go wrong? What is irreversible?
- Are there safer or simpler alternatives?

Do this thinking out loud in a short paragraph or bullet list. It doesn't need to be
long — just enough so the user can see your reasoning and catch misunderstandings early.

### 2. Say (present the plan)

Present a numbered action plan. Each step should be concrete enough that the user
can predict exactly what will happen. For commands and tool calls, show the actual
invocation, not a vague description.

**Format:**

```
## Plan

1. [action type] — brief rationale
   `command or tool call here`

2. [action type] — brief rationale
   `command or tool call here`

⚠️  Step 3 is irreversible: [explain why]
3. [action type] — brief rationale
   `command or tool call here`
```

Flag steps that are irreversible, destructive, or affect shared state with a ⚠️ warning.

**Action types to label:**
- `[read]` — reading files, grepping, listing
- `[write]` — creating or overwriting files
- `[edit]` — modifying existing files
- `[run]` — shell commands
- `[delete]` — removing files or data
- `[network]` — HTTP requests, git push/pull, API calls
- `[other]` — anything else

### 3. Approve

End the plan with an explicit approval prompt:

```
Shall I proceed with this plan? You can say "yes", approve specific steps ("do steps
1-3"), or ask me to adjust anything before I start.
```

Then **stop and wait**. Do not begin executing until the user responds affirmatively.
If they ask to change something, update the plan and present it again before proceeding.

### 4. Do

Execute the approved steps in order. After each step, briefly confirm what happened
(one line is fine). If anything unexpected occurs mid-execution, pause and report
before continuing.

---

## Key constraints

- Never collapse the loop. Even for "obviously safe" reads or lookups, present the plan
  first when this skill is active. The user invoked this skill because they want
  visibility — don't second-guess that.

- Never batch the approval. Don't say "I'll go ahead and do X while asking about Y."
  The whole plan goes up front; execution starts only after approval.

- Keep the plan honest. If you're not sure exactly what a command will do, say so
  explicitly in the plan rather than papering over uncertainty.

- Partial approval is fine. If the user approves only some steps, execute only those.
  Re-present the remaining steps as a new plan before asking again.

---

## Example

**User:** df-think-say-approve-do — clean up the old log files in /var/app/logs

**Thinking:**

The task is to remove old log files. I should check what's there first, understand the
naming pattern, and confirm before deleting anything — deletions are irreversible.

**Plan:**

1. [read] Survey what's in the log directory
   `ls -lh /var/app/logs/`

2. [read] Check the oldest files to understand the date range
   `ls -lt /var/app/logs/ | tail -20`

⚠️  Step 3 is irreversible: deleted log files cannot be recovered without a backup.
3. [delete] Remove log files older than 30 days
   `find /var/app/logs/ -name "*.log" -mtime +30 -delete`

Shall I proceed with this plan? You can say "yes", approve specific steps ("do steps
1-2 first"), or ask me to adjust anything.