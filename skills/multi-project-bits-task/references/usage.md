# Multi-project BITS Task Usage

## Purpose

This skill captures a business-specific workflow for multiple BITS development task templates.

It should also trigger when the user talks about deployment or environment in a BITS-task context, for example:

- “deploy to ppe_cue_agent”
- “set environment to ppe_cue_lsl_test”
- “deployment environment is symphony_mock_sse”

## Project presets

- Default project: `Creative Cue`
- Default lane: `test`
- Default environment (mapped to lane): `ppe_cue_agent`

## Environment presets

In this skill, “environment” means the BITS `lane` used during `bits develop create`.

- `cue_agent` -> `ppe_cue_agent`
- `symphony_mock_sse` -> `ppe_symphony_mock_sse`
- Any raw `ppe_*` env is passed through directly, e.g. `ppe_cue_lsl_test`

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
node /Users/bytedance/.config/opencode/skills/multi-project-bits-task/scripts/create-bits-rd-task.mjs <meego-or-url>
```

## Common examples

```bash
# Dry-run with auto title / branch / developer
node /Users/bytedance/.config/opencode/skills/multi-project-bits-task/scripts/create-bits-rd-task.mjs 6877090179

# Real create
node /Users/bytedance/.config/opencode/skills/multi-project-bits-task/scripts/create-bits-rd-task.mjs 6877090179 --create

# AI Editor Vibe with preset template dev-id
node /Users/bytedance/.config/opencode/skills/multi-project-bits-task/scripts/create-bits-rd-task.mjs --project vibe --meego 6877090179

# Use symphony mock SSE deploy environment
node /Users/bytedance/.config/opencode/skills/multi-project-bits-task/scripts/create-bits-rd-task.mjs --env symphony_mock_sse --meego 6877090179

# Use a raw PPE environment directly
node /Users/bytedance/.config/opencode/skills/multi-project-bits-task/scripts/create-bits-rd-task.mjs --env ppe_cue_lsl_test --meego 6877090179

# creative-bff-i18n with preset template dev-id
node /Users/bytedance/.config/opencode/skills/multi-project-bits-task/scripts/create-bits-rd-task.mjs --project creative-bff-i18n --meego 6877090179

# Override title
node /Users/bytedance/.config/opencode/skills/multi-project-bits-task/scripts/create-bits-rd-task.mjs 6877090179 "Creative Cue hotfix"

# Override developer if git config email is not the desired value
node /Users/bytedance/.config/opencode/skills/multi-project-bits-task/scripts/create-bits-rd-task.mjs 6877090179 --developer liusenlin0927@bytedance.com
```

## Notes

- The script defaults to dry-run.
- Only `--create` performs an actual BITS create action.
- If `--env` is omitted, the script uses lane `ppe_cue_agent` during create.
- `--env symphony_mock_sse` maps to lane `ppe_symphony_mock_sse` during create.
- `--env ppe_cue_lsl_test` passes through as lane `ppe_cue_lsl_test` during create.
- If `--lane` is explicitly provided, it overrides the lane derived from `--env`.
- If BITS rejects the request, return the raw API error instead of guessing.
