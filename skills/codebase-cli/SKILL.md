---
name: codebase-cli
description: "Interact with Codebase (a.k.a NextCode, Code) via the `codebase` CLI. Use when the user asks to manage merge requests, issues, labels, repositories, code reviews, create MRs, check MR status, comment on MRs/issues, read remote files, investigate CI failures, check pipeline results, search code across repositories, find function definitions, search commit history, or perform any task involving code.byted.org. Triggers on keywords: MR, merge request, issue, code review, codebase, repo, label, diff, review, CI, pipeline, check, failed check, search code, find function, cross-repo search."
allowed-tools: Bash(codebase *)
---

# Codebase CLI Skill

Use the `codebase` CLI to interact with code management platform (code.byted.org).

## Installation & Invocation

### Prerequisites

- **Node.js**: Node.js >= 20.12.0
- **Registry**: Prefer the internal registry `http://bnpm.byted.org`

### Check global command

Codebase CLI Version: !`codebase --version`

If Codebase CLI Version **NOT** a valid version like "@vecode-fe/codebase-cli/1.0.0 darwin-arm64 node-v22.14.0", **YOU MUST** ask user to install `codebase` in global via:

```bash
npm install -g @vecode-fe/codebase-cli@latest --registry=http://bnpm.byted.org
```

If not installed, fall back to `npx` for temporary usage:

```bash
npx --registry=http://bnpm.byted.org @vecode-fe/codebase-cli <command>
```

## Core Principles

- **JSON Output**: Commands return a single JSON object. **Exception: `codebase search code` outputs NDJSON — one JSON object per line. Parse each line independently; do NOT parse the entire output as one JSON value.**
- **Command Pattern**: `codebase <resource> <action> [flags]`. Use explicit flags (e.g., `-N`, `-R`).
- **Repository Context**: Auto-detects from current git remote. Use `-R <repo_path>` (e.g., `-R nextcode/codebase-cli`) for other repos.
- **Flag Discovery**: Run `codebase <command> --help` only for subcommands not documented in the Command Reference below.
- **Dangerous Operations**: Destructive commands (`mr merge`, `mr bypass`, `issue delete`, etc.) require `--yes`. **You MUST obtain explicit user confirmation before executing any command with `--yes`.** Use `--dry-run` when available.
- **Provide URL**: After creating MR or Issue, compose: `https://code.byted.org/${repo_path}/merge_requests/${n}` or `.../issues/${n}`.
- **Search vs List**: Use `codebase search mr` / `codebase search issue` for cross-repository queries or user-centric filters (`--attention @me`, `--author @me`, `--assignee @me`). Use `codebase mr list` / `codebase issue list` only when the target repository is known.
- **Use jq to filter**: Pipe output through `jq` to extract only what you need — avoids unnecessary token overhead.

## CLI Structure

```
codebase
├── mr          list · view · diff · status · create · edit · close · reopen · merge† · bypass†
│   ├── comment   list · create · reply · resolve · unresolve · delete† · publish
│   └── checks    list · view · trigger
├── issue       list · view · create · edit · close · reopen · delete†
│   └── comment   list · create · reply · resolve · unresolve · delete†
├── repo        view · edit
│   ├── file         list · cat · commit
│   ├── member       list · view · invite · edit · remove† · leave†
│   ├── protected-branch  list · view · create · delete†
│   └── protected-tag     list · view · create · delete†
├── label       list · create · edit · delete†
├── tag         list · view · create · delete†
├── search      code · mr · issue
└── auth        login · logout · status
```

(†) Destructive — requires `--yes` and explicit user confirmation before executing.

## Command Reference

### Merge Requests

```bash
# List — output: {MergeRequests:[{Number,Status,Draft,Title,SourceBranchName,TargetBranchName,URL,CreatedBy,CreatedAt,UpdatedAt}], TotalCount}
codebase mr list -R <repo> [--status open|closed|merged] [--author <user>] [--reviewer <user>]
                            [--label <name>] [--page-size <n>] [--sort-by CreatedAt|UpdatedAt|Id] [--sort-order Asc|Desc]
# Count all:        | jq '.TotalCount'
# Titles+numbers:   | jq '[.MergeRequests[] | {number:.Number, title:.Title, status:.Status}]'
# Most recent:      default sort is UpdatedAt Desc → .MergeRequests[0]
# Smallest number:  --sort-by Id --sort-order Asc --page-size 1 → .MergeRequests[0]

# View
codebase mr view -N <n> [-R <repo>]

# Diff
codebase mr diff -N <n> [-R <repo>] [--name-only] [--stat] [--file <path>...]

# Mergeability + review summary (NOT CI detail — use mr checks list for CI)
codebase mr status -N <n> [-R <repo>]

# CI check runs
codebase mr checks list -N <n> [-R <repo>]

# Comments
codebase mr comment list -N <n> [-R <repo>] [--resolved] [--unresolved]
# Count: | jq '.Threads | length'
```

### Issues

```bash
# List — output: {Issues:[{Number,Status,Title,CreatedBy,CreatedAt,UpdatedAt}], TotalCount}
codebase issue list -R <repo> [--status backlog|todo|in_progress|done|canceled]
                               [--assignee <user>] [--label <name>] [-q <query>] [--page-size <n>]
# Count:          | jq '.TotalCount'
# Titles+numbers: | jq '[.Issues[] | {number:.Number, title:.Title, status:.Status}]'

# View
codebase issue view -N <n> [-R <repo>]
```

### Repository

```bash
codebase repo view [-R <repo>]
codebase repo file list [-R <repo>] [--path <dir>] [--ref <branch|tag|sha>]
codebase repo file cat  [-R <repo>] --path <file> [--ref <branch|tag|sha>]
codebase repo protected-branch list [-R <repo>]   # only way to list branches
```

### Labels & Tags

```bash
codebase label list [-R <repo>]
codebase tag list   [-R <repo>] [-q <query>] [--page-size <n>]
# Tag names: | jq '[.Tags[].Name]'
```

### Cross-Repo Search

```bash
# MRs — output: {MergeRequests:[{Number,Status,Title,...}], NextPageToken}
codebase search mr [--attention <user|@me>] [--author <user>] [--status open|closed|merged]
                   [--repo-path <repo>] [--page-size <n>]

# Issues — output: {Issues:[{Number,Status,Title,...}], NextPageToken}
codebase search issue [--assignee <user|@me>] [--author <user>] [--status open|...]
                      [-q <query>] [--repo-path <repo>] [--page-size <n>]
```

## Authentication

If a command fails with an auth error, or `codebase auth status` shows no authenticated identity:

1. Prompt the user to run `codebase auth login`.
2. If that fails **and** the environment variable `CI_WORKSPACE` is **not set**, try the following fallback:

```bash
# IMPORTANT: never print or echo the JWT value — treat it as a secret
if _jwt=$(npx --registry=https://bnpm.byted.org -y skills get-codebase-jwt 2>/dev/null) && [ -n "$_jwt" ]; then
  codebase auth login --jwt "$_jwt"
  unset _jwt
else
  unset _jwt
  echo "Failed to obtain JWT. Please run 'codebase auth login' manually."
fi
```

After `codebase auth login --jwt` succeeds, the token is stored in the OS keychain. If auth still fails, ask the user to log in manually.

## Key Workflows

### Search Code Across Repositories

**Output format (NDJSON — parse each line independently):**

```
{"type":"result","repo":"myteam/myrepo","file":"src/main.go","line":42,"content":"func main() {","lang":"Go"}
{"type":"alert","title":"...","description":"..."}   # only when server sends a warning
{"type":"done","count":42,"limited":false}           # final line; if limited:true, increase --limit
```

**Examples:**

```bash
codebase search code "func HttpHandler lang:Go repo:myteam/myrepo"
codebase search code "TODO lang:Go -file:_test.go department:my_department" --limit 10
codebase search code "HttpHandler type:symbol" --limit 5
codebase search code "fix memory leak type:commit" --limit 5
codebase search code "panic lang:Go" --pattern regexp --limit 20
```

**Key inline filters:** `lang:Go` `repo:path/name` `file:.go$` `type:symbol|commit|diff|repo|path` `department:name` `rev:main` `author:username` `after:"2 weeks ago"` `case:yes` `-lang:Go` (negate with `-`)

**Flags:** `--limit N` (default 30), `--pattern literal|regexp|structural`

### Code Review Workflow (full review — not needed for simple `mr view`)

1. `codebase mr view -N <n>` — title, description, author, branches.
2. `codebase mr diff -N <n> --name-only` — changed file list; `--file <path>` for focused diff.
3. `codebase mr status -N <n>` — mergeability and review summary.
4. `codebase mr checks list -N <n>` — CI results; inspect `Text` field for ✅/❌ step markers.
5. `codebase mr comment create -N <n> --body <feedback>` — `--path`/`--start-line`/`--end-line` for inline.
6. `codebase mr review -N <n> --approve` — or `--disapprove`, `--dismiss`.

### Investigate CI / Check Failures

1. `codebase mr checks list -N <n>` — list all runs; look for `Conclusion != "succeeded"`.
2. Inspect the `Text` field of failed checks — Markdown with ✅/❌/⏺ per step.
3. `codebase mr checks view` — single check detail if needed.

## Best Practices

1. **Investigate Before Acting**: Always `view` + `diff` before reviewing or merging.
2. **Don't Dump JSON**: Parse output silently; synthesize natural language responses.
3. **Filter Progressively**: Use `--page-size` to limit results; pipe to `jq` to extract only needed fields.
4. **`--yes` Requires User Consent**: NEVER pass `--yes` to destructive commands without explicit user confirmation.
