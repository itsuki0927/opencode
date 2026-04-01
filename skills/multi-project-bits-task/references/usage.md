# Multi-project BITS Task Usage

## Purpose

This skill captures a business-specific workflow for multiple BITS development task templates.

## Project presets

- Default project: `Creative Cue`
- Default lane: `test`

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
- If BITS rejects the request, return the raw API error instead of guessing.
