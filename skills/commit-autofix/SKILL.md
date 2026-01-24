---
name: commit-autofix
description: |
  AI-assisted git commit with automatic error fixing.
  Triggers: /commit command, xcommit failures, TypeScript/ESLint errors.
  Focus: TypeScript (.ts) and TypeScriptReact (.tsx) and Css(.css/.scss/.less) files.
---

# Commit AutoFix

## Workflow

### Step 1: Execute xcommit

```bash
xcommit
```

Capture stdout and stderr from the command.

### Step 2: Handle Result

**If successful (exit code 0)**:
Go to Step 4 to output Summary, then **auto-push** (Step 5a).

**If failed**:

1. Display notification:
   ```
   ⚠️ Errors detected, attempting to fix...
   ```
2. Pass the complete error output to AI for analysis
3. AI reads related files and fixes issues (focus on .ts/.tsx files)
4. After fixing, `git add` the modified files

### Step 3: Retry (max 2 times)

Re-execute `xcommit`, repeat Step 2.

### Step 4: Output Summary

**On success**:

```
✅ Commit successful!

Summary:
- Commit: <hash>
- Message: <commit message>
- Fixed files: <list> (if any)
```

**On failure**:

```
❌ Commit failed

Summary:
- Attempts: 3
- Remaining errors:
  <error output>
- Suggestion: Please manually check the above errors
```

### Step 5: Push to Remote

**Only execute this step after commit succeeds.**

#### Step 5a: Auto-Push (First attempt succeeded without fixes)

If xcommit succeeded on the **first attempt** (no errors, no fixes needed):

1. Automatically execute `git push`
2. Display push result
3. No confirmation needed

#### Step 5b: Ask Push (Succeeded after fixing errors)

If xcommit succeeded **after fixing errors** (retry was needed):

Ask user whether to push to remote:

```
🚀 Would you like to push this commit to remote?
```

**If user confirms push**:

1. Execute `git push`
2. Display push result

**If user declines**:
End workflow.

## Guardrails

- Maximum 2 retries (3 total attempts)
- Do not fix unit test failures
- Do not use --no-verify
- Focus on TypeScript/TypeScriptReact files
- Auto-push on first-attempt success; ask confirmation only after error fixes
