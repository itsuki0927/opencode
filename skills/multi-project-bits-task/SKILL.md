---
name: multi-project-bits-task
description: >-
  为多个创意项目创建 BITS 研发任务的固定业务模板。只要用户提到创建 Creative Cue、AI Editor Vibe、creative-bff-i18n 的研发任务、BITS 开发任务、dev task，或者希望从当前 git 仓库自动读取分支、commit 标题、developer 并只手动输入 Meego，就应该使用这个 skill。支持用自然语言指定项目名或别名，并优先执行 dry-run；只有用户明确要求真实创建时才执行 create。
user-invocable: true
allowed-tools: Bash
---

# 多项目 BITS 研发任务模板

这个 skill 用于把多个项目的常用 BITS 创建流程固化成一个可复用模板。

## 项目预设

- 默认项目：`Creative Cue`
- 默认 `lane`: `test`

当前内置项目：

1. `Creative Cue`
   - aliases: `creative cue`, `creative-cue`, `cue`
   - `service`: `Creative Cue`
   - `from-dev-id`: `2165655`
   - `service-type`: `PROJECT_TYPE_WEB`

2. `AI Editor Vibe`
   - aliases: `ai editor vibe`, `ai-editor-vibe`, `editor vibe`, `vibe`
   - `service`: `AI Editor Vibe`
   - `from-dev-id`: `2165655`
   - `service-type`: `PROJECT_TYPE_WEB`

3. `creative-bff-i18n`
   - aliases: `creative-bff-i18n`, `creative bff i18n`, `bff i18n`, `creative bff`
   - `service`: `creative-bff-i18n`
   - `from-dev-id`: `2165655`
   - `service-type`: `PROJECT_TYPE_WEB`

## 自动读取的字段

默认从当前 git 仓库读取：

- `title` → `git log -1 --pretty=%s`
- `branch` → `git rev-parse --abbrev-ref HEAD`
- `developer` → `git config user.email`

`meego` 需要用户手动提供，支持 ID 或 URL。

## 执行原则

1. 默认先执行 dry-run。
2. 如果用户用自然语言指定项目名，先映射到内置项目别名，再调用脚本时传 `--project`。
3. 只有当用户明确说“正式创建”“直接创建”“不要 dry-run”时，才追加 `--create`。
4. 如果脚本输出失败，优先把错误原样返回给用户，不要猜测 BITS 的隐藏规则。

## 使用方式

优先调用脚本：

```bash
node /Users/bytedance/.config/opencode/skills/multi-project-bits-task/scripts/create-bits-rd-task.mjs <meego-or-url>
```

指定项目：

```bash
node /Users/bytedance/.config/opencode/skills/multi-project-bits-task/scripts/create-bits-rd-task.mjs --project vibe <meego-or-url>
node /Users/bytedance/.config/opencode/skills/multi-project-bits-task/scripts/create-bits-rd-task.mjs --project creative-bff-i18n <meego-or-url>
```

真实创建：

```bash
node /Users/bytedance/.config/opencode/skills/multi-project-bits-task/scripts/create-bits-rd-task.mjs <meego-or-url> --create
```

可选覆盖：

```bash
node /Users/bytedance/.config/opencode/skills/multi-project-bits-task/scripts/create-bits-rd-task.mjs <meego-or-url> "title override"
node /Users/bytedance/.config/opencode/skills/multi-project-bits-task/scripts/create-bits-rd-task.mjs --meego <meego> --branch <branch> --developer <email>
node /Users/bytedance/.config/opencode/skills/multi-project-bits-task/scripts/create-bits-rd-task.mjs --project <project> --meego <meego>
```

## 给用户的输出

执行后，简要告诉用户：

- 解析出的 `title`、`branch`、`developer`
- 解析出的 `project`、`service`、`from-dev-id`、`service-type`
- 是否是 dry-run
- 如果真实创建成功，返回 `dev task ID` 和 BITS 链接

## 参考

如需看底层参数与示例，参考：

- `@references/usage.md`
