# Multi-project BITS Task Usage

## Purpose

This skill captures a business-specific workflow for multiple BITS development task templates.

It should also trigger when the user talks about deployment or environment in a BITS-task context, for example:

- “deploy to ppe_cue_agent”
- “set environment to ppe_cue_lsl_test”
- “deployment environment is symphony_mock_sse”

## Project presets

- Default project: `Creative Cue`
- Default Meego: `7034929152`
- Default lane: `test`
- Default environment (mapped to lane): `ppe_cue_<developer-name>`

## Environment presets

In this skill, “environment” means the BITS `lane` used during `bits develop create`.

- Default omitted env -> `ppe_cue_<developer-name>` derived from `developer`
- `cue_agent` -> `ppe_cue_agent` when explicitly passed
- `symphony_mock_sse` -> `ppe_symphony_mock_sse`
- Any raw `ppe_*` env is passed through directly, e.g. `ppe_cue_lsl_test`

Developer name derivation uses the `developer` value, which defaults to `git config user.email`: take the part before `@`, drop any `+` suffix, remove trailing digits, lowercase it, and replace non-alphanumeric characters with `_`. Example: `liusenlin0927@bytedance.com` -> `ppe_cue_liusenlin`.

## Remote branch preflight

BITS validates that the `--scm-branch` value exists on the remote repository. Before calling `bits develop create`, the script checks whether `origin/<branch>` exists.

- Dry-run: never pushes; reports that a missing branch would be pushed during real create.
- Real create: if the current checkout branch is missing on `origin`, runs `git push -u origin <branch>:<branch>` before creating the BITS task.
- Explicit `--branch` pointing to a branch other than the current checkout branch: skips auto-push to avoid pushing the wrong local branch.
- Use `--remote <remote>` to check and push a remote other than `origin`.

### Creative Cue

- service: `Creative Cue`
- from-dev-id: `2165655`
- service-type: `PROJECT_TYPE_WEB`

### AI Editor Vibe

- service: `AI Editor Vibe`
- from-dev-id: `2165655`
- service-type: `PROJECT_TYPE_WEB`

### creative-bff-i18n

- service: `creative-bff-i18n`
- from-dev-id: `2165655`
- service-type: `PROJECT_TYPE_WEB`

## Script path

```bash
node /Users/bytedance/.config/opencode/skills/multi-project-bits-task/scripts/create-bits-rd-task.mjs
```

## Common examples

```bash
# Dry-run with auto title / branch / developer
node /Users/bytedance/.config/opencode/skills/multi-project-bits-task/scripts/create-bits-rd-task.mjs

# Real create
node /Users/bytedance/.config/opencode/skills/multi-project-bits-task/scripts/create-bits-rd-task.mjs --create

# Real create with a non-origin remote
node /Users/bytedance/.config/opencode/skills/multi-project-bits-task/scripts/create-bits-rd-task.mjs --remote code --create

# AI Editor Vibe with preset template dev-id
node /Users/bytedance/.config/opencode/skills/multi-project-bits-task/scripts/create-bits-rd-task.mjs --project vibe

# Use symphony mock SSE deploy environment
node /Users/bytedance/.config/opencode/skills/multi-project-bits-task/scripts/create-bits-rd-task.mjs --env symphony_mock_sse

# Use a raw PPE environment directly
node /Users/bytedance/.config/opencode/skills/multi-project-bits-task/scripts/create-bits-rd-task.mjs --env ppe_cue_lsl_test

# creative-bff-i18n with preset template dev-id
node /Users/bytedance/.config/opencode/skills/multi-project-bits-task/scripts/create-bits-rd-task.mjs --project creative-bff-i18n

# Override title
node /Users/bytedance/.config/opencode/skills/multi-project-bits-task/scripts/create-bits-rd-task.mjs --title "Creative Cue hotfix"

# Override developer if git config email is not the desired value
node /Users/bytedance/.config/opencode/skills/multi-project-bits-task/scripts/create-bits-rd-task.mjs --developer liusenlin0927@bytedance.com
```

## Notes

- The script defaults to dry-run.
- If `--meego` or positional Meego is omitted, the script uses Meego `7034929152`.
- Only `--create` performs an actual BITS create action.
- On real create, a missing remote current branch is pushed before calling BITS to avoid `branch_not_found`.
- Dry-run never pushes; it only reports the branch preflight result.
- If `--env` is omitted, the script uses lane `ppe_cue_<developer-name>` during create.
- `--env symphony_mock_sse` maps to lane `ppe_symphony_mock_sse` during create.
- `--env ppe_cue_lsl_test` passes through as lane `ppe_cue_lsl_test` during create.
- If `--lane` is explicitly provided, it overrides the lane derived from `--env`.
- If BITS rejects the request, return the raw API error instead of guessing.
