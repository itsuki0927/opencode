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
- **Registry**: Prefer the internal registry `http://bnpm.byted.org` for both `npx`, `npm install`, `pnpm`, `bun`, etc.

### Check global command
Codebase CLI Version: !`codebase --version`

If Codebase CLI Version **NOT** a valid version like "@vecode-fe/codebase-cli/1.0.0 darwin-arm64 node-v22.14.0", **YOU MUST** ask user to install `codebase` in global via:

```bash
npm install -g @vecode-fe/codebase-cli@latest --registry=http://bnpm.byted.org
```

### Use CLI

Prefer using the `codebase` command directly.
```bash
codebase <command>
```
If it is not installed (command not found), fall back to `npx` for temporary usage:

```bash
npx --registry=http://bnpm.byted.org @vecode-fe/codebase-cli <command>
```

For example: `npx --registry=http://bnpm.byted.org @vecode-fe/codebase-cli --help`

### Update
If use require update `codebase`, should use `npx --registry=http://bnpm.byted.org @vecode-fe/codebase-cli --version` check version.

If need update, use `npm install -g @vecode-fe/codebase-cli@latest --registry=http://bnpm.byted.org`.

## Core Principles

- **JSON Output**: Most commands (exclude `codebase setup`) return a single JSON object. **Exception: `codebase search code` outputs NDJSON — one JSON object per line, streamed as results arrive. Parse each line independently; do NOT attempt to parse the entire output as one JSON value.**
- **Command Pattern**: `codebase <resource> <action> [flags]`. Use explicit flags (e.g., `-N`, `-R`) instead of positional arguments.
- **Repository Context**: The CLI auto-detects the repo from the current git remote. Use `-R <repo_path_or_id>` (e.g., `-R nextcode/codebase-cli`) when targeting a different repo.
- **Flag Discovery**: **ALWAYS run `codebase <command> --help` before executing any unfamiliar command.** Never guess flags or subcommand names. The help output is the source of truth.
- **Dangerous Operations**: Destructive commands (`mr merge`, `mr bypass`, `issue delete`, etc.) require `--yes` flag. **You MUST obtain explicit user confirmation before executing any command with `--yes`.** Never auto-approve destructive actions. Use `--dry-run` when available to preview first.
- **Provide URL**: After created MR or Issue, you should tell user the web url, you can compose it use repository path, number like `https://code.byted.org/${repository_path}/issues/${number}`
- **Search vs List**: Use `codebase search mr` / `codebase search issue` for cross-repository queries or any user-centric filter (`--me`, `--attention`, `--reviewer`, `--author`). Use `codebase mr list` / `codebase issue list` only when the target repository is explicitly known.

## Authentication

If a command fails with an auth error, or `codebase auth status` shows no authenticated identity:

1. Prompt the user to run `codebase auth login`.
2. If that fails **and** the environment variable `CI_WORKSPACE` is **not set** (i.e. non-CI environment), try the following fallback to obtain a JWT automatically:

```bash
# Check auth status first
codebase auth status

# If no identity found, attempt to fetch a JWT via the internal skills helper and log in directly
# IMPORTANT: never print or echo the JWT value — treat it as a secret
if _jwt=$(npx --registry=https://bnpm.byted.org -y skills get-codebase-jwt 2>/dev/null) && [ -n "$_jwt" ]; then
  codebase auth login --jwt "$_jwt"
  unset _jwt
else
  unset _jwt
  echo "Failed to obtain JWT. Please run 'codebase auth login' manually."
fi
```

**Security**: Never print, log, or display the JWT value. Treat it as a secret credential.

After `codebase auth login --jwt` succeeds, the token is stored in the OS keychain and subsequent commands will authenticate automatically. If auth still fails, ask the user to log in manually.

## Available Resources
Run `codebase --help` for the full command tree.

## Key Workflows

### Search Code Across Repositories

Use `codebase search code "<query>"` for cross-repository full-text, symbol, path, commit, or repo search. Requires JWT auth.

**Output format (NDJSON — parse each line independently):**
```
{"type":"result","repo":"myteam/myrepo","file":"src/main.go","line":42,"content":"func main() {","lang":"Go"}
{"type":"alert","title":"...","description":"..."}   # only when server sends a warning
{"type":"done","count":42,"limited":false}           # final line; if limited:true, increase --limit
```

**All filters go inside the quoted query string:**
```bash
codebase search code "func HttpHandler lang:Go repo:myteam/myrepo"
codebase search code "TODO lang:Go -file:_test.go department:my_department" --limit 10
codebase search code "HttpHandler type:symbol" --limit 5
codebase search code "fix memory leak type:commit" --limit 5
codebase search code "myteam/myrepo type:repo"
codebase search code "panic lang:Go" --pattern regexp --limit 20
```

**Key inline filters:** `lang:Go` `repo:path/name` `file:.go$` `type:symbol|commit|diff|repo|path` `department:my_department` `rev:main` `author:username` `after:"2 weeks ago"` `case:yes` `-lang:Go` (negate with `-`)

**Flags:** `--limit N` (default 30; increase if `done.limited:true`), `--pattern literal|regexp|structural`, `--type file|symbol|path|commit|diff|repo`

### Review a MR
1. `codebase mr view -N <n>` — Get MR metadata (title, description, author, branches).
2. `codebase mr diff -N <n>` — Get the full diff. Use `--name-only` for a file list, `--file <path>` to focus on specific files.
3. `codebase mr status -N <n>` — Check mergeability and review status. **Only returns a CI summary; use `mr checks list` for detailed check results.**
4. `codebase mr comment create -N <n> --body <feedback>` — Leave a summary comment. Add `--path`, `--start-line`, `--end-line` for inline diff comments.
5. `codebase mr review -N <n> --approve` — Approve (or `--disapprove`, `--dismiss`).

### Investigate CI / Check Failures
When the user asks about failing CI, failing checks, or why a check failed:
1. `codebase mr checks list -N <n>` — List all check runs with status and conclusion. Filter for `Conclusion != "succeeded"` to find failures.
2. Inspect the `Text` field of each failed check — it contains per-step results in Markdown, with ✅/❌/⏺ markers indicating pass/fail/skipped steps. Parse it to identify the exact failing step and its exit code or error message.
3. `codebase mr checks view` — View a single check run in detail if needed.

### Browse Repository Files
Use `codebase repo file list` and `codebase repo file cat` to explore remote file content.

```bash
# List files in root directory
codebase repo file list -R <repo_path>

# List files in a subdirectory
codebase repo file list -R <repo_path> --path src/

# Read file content
codebase repo file cat -R <repo_path> --path README.md

# Read file at a specific branch/tag/commit
codebase repo file cat -R <repo_path> --path main.go --ref main
```

**Note**: There is no command to list all branches. Use `codebase repo protected-branch list -R <repo_path>` to list protected branches only.

## Best Practices

1. **Investigate Before Acting**: Always `view` + `diff` before reviewing or merging.
2. **Don't Dump JSON**: Parse output silently; synthesize natural language responses.
3. **Use `--help` Liberally**: When unsure about flags, run `codebase <command> --help`.
4. **Use `--dry-run`**: Preview merge/create results before committing to an action.
5. **`--yes` Requires User Consent**: NEVER pass `--yes` to destructive commands (`mr merge`, `mr bypass`, `issue delete`, etc.) without first asking the user for explicit confirmation. Always describe what the command will do and wait for approval.
6. **Fetch Progressively for Large Output**: `--verbose` can produce very large payloads. Start with a smaller `--page-size` to understand response structure, then use `jq` to extract only required fields instead of processing the full output.
