---
name: multi-project-bits-task
description: >-
  为多个创意项目创建 BITS 研发任务的固定业务模板。只要用户提到创建 Creative Cue、AI Editor Vibe、creative-bff-i18n 的研发任务、BITS 开发任务、dev task，或者希望从当前 git 仓库自动读取分支、commit 标题、developer 并使用默认 Meego，就应该使用这个 skill。也适用于用户用“部署到某个环境”“发到某个环境”“把环境设成 ppe_xxx”“部署环境是 ppe_xxx”这类说法来表达 BITS 创建时的 lane 诉求。支持用自然语言指定项目名或别名；如果用户未指定环境，默认使用 `ppe_cue_<开发者英文名>`；并优先执行 dry-run；真实创建前会检查远程当前分支，缺失时先 push 避免 BITS branch_not_found；只有用户明确要求真实创建时才执行 create。
user-invocable: true
allowed-tools: Bash
---

# 多项目 BITS 研发任务模板

这个 skill 用于把多个项目的常用 BITS 创建流程固化成一个可复用模板。

## 项目预设

- 默认项目：`Creative Cue`
- 默认 `meego`: `7034929152`
- 默认 `lane`: `test`
- 默认环境（映射到 lane）：`ppe_cue_<开发者英文名>`

## 环境预设

这里的“环境”指的是 BITS 创建时使用的 `lane`。也就是说，用户说“把环境设成 `ppe_cue_lsl_test`”，实际应理解为创建命令里的 `--lane ppe_cue_lsl_test`。

- 默认 `env`: 由 `developer` 推导，格式为 `ppe_cue_<开发者英文名>`
- `symphony_mock_sse` → `ppe_symphony_mock_sse`
- 也支持直接传任意 `ppe_*` 环境名，例如 `ppe_cue_lsl_test`

开发者英文名从 `developer`（默认 `git config user.email`）推导：取邮箱 `@` 前缀、去掉 `+` 后缀、去掉末尾数字、转小写并把非字母数字字符转成 `_`。例如 `liusenlin0927@bytedance.com` → `ppe_cue_liusenlin`。

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

`meego` 默认使用 `7034929152`，用户也可以手动提供 ID 或 URL 覆盖。

## 远程分支预检查

BITS 创建使用 `--scm-mode branch` + `--scm-branch <branch>`，平台会校验远端分支是否存在。脚本在调用 BITS 前会检查默认远端 `origin` 上是否存在当前分支：

- 如果远端分支已存在：直接继续创建。
- 如果远端分支不存在且是 dry-run：不做 push，只在输出的 `branchPreflight` 中提示真实创建时会 push。
- 如果远端分支不存在且是真实创建：先执行 `git push -u origin <branch>:<branch>`，成功后再创建 BITS 研发任务。
- 如果用户用 `--branch` 指定了非当前 checkout 分支：跳过自动 push，避免把错误本地分支推到远端；这类场景需用户自行确保远端分支存在。
- 如需使用其他远端，传 `--remote <remote>`。

## 执行原则

1. 默认先执行 dry-run。
2. 如果用户用自然语言指定项目名，先映射到内置项目别名，再调用脚本时传 `--project`。
3. 如果用户指定 `env` / 环境：
   - `symphony_mock_sse` 映射到 `ppe_symphony_mock_sse`
   - 如果本身就是 `ppe_*` 环境名，则直接透传
   - 未指定时默认使用 `ppe_cue_<开发者英文名>`
4. 脚本调用时通过 `--env <value>` 传入环境别名，脚本内部优先把它转换成创建命令的 `--lane`；只有用户显式传了 `--lane` 时才以用户提供值为准。
5. 真实创建前允许脚本自动检查并 push 缺失的远端当前分支，避免 BITS 返回 `branch_not_found`。
6. 只有当用户明确说“正式创建”“直接创建”“不要 dry-run”时，才追加 `--create`。
7. 如果脚本输出失败，优先把错误原样返回给用户，不要猜测 BITS 的隐藏规则。

## 使用方式

用户常见说法可以直接按下面理解：

- “部署到 `ppe_cue_agent`” → 视为设置 BITS `lane`
- “环境是 `ppe_cue_lsl_test`” → 视为设置 BITS `lane`
- “部署环境用 `symphony_mock_sse`” → 先映射到 `ppe_symphony_mock_sse`，再作为 `lane`
- 未指定环境 → 根据 `developer` 默认生成 `ppe_cue_<开发者英文名>`

优先调用脚本：

```bash
node /Users/bytedance/.config/opencode/skills/multi-project-bits-task/scripts/create-bits-rd-task.mjs
```

指定项目：

```bash
node /Users/bytedance/.config/opencode/skills/multi-project-bits-task/scripts/create-bits-rd-task.mjs --project vibe
node /Users/bytedance/.config/opencode/skills/multi-project-bits-task/scripts/create-bits-rd-task.mjs --project creative-bff-i18n
node /Users/bytedance/.config/opencode/skills/multi-project-bits-task/scripts/create-bits-rd-task.mjs --env symphony_mock_sse
node /Users/bytedance/.config/opencode/skills/multi-project-bits-task/scripts/create-bits-rd-task.mjs --env ppe_cue_lsl_test
```

真实创建：

```bash
node /Users/bytedance/.config/opencode/skills/multi-project-bits-task/scripts/create-bits-rd-task.mjs --create
```

可选覆盖：

```bash
node /Users/bytedance/.config/opencode/skills/multi-project-bits-task/scripts/create-bits-rd-task.mjs --title "title override"
node /Users/bytedance/.config/opencode/skills/multi-project-bits-task/scripts/create-bits-rd-task.mjs --meego <meego> --branch <branch> --developer <email>
node /Users/bytedance/.config/opencode/skills/multi-project-bits-task/scripts/create-bits-rd-task.mjs --project <project> --meego <meego>
node /Users/bytedance/.config/opencode/skills/multi-project-bits-task/scripts/create-bits-rd-task.mjs --project <project> --env <env> --meego <meego>
node /Users/bytedance/.config/opencode/skills/multi-project-bits-task/scripts/create-bits-rd-task.mjs --remote <remote>
```

## 给用户的输出

执行后，简要告诉用户：

- 解析出的 `title`、`branch`、`developer`
- 远程分支预检查结果 `branchPreflight`，包括是否已存在、是否 push、是否跳过
- 解析出的 `project`、`service`、`from-dev-id`、`service-type`
- 解析出的 `env`、目标部署环境、最终生效的 `lane`
- 是否是 dry-run
- 如果真实创建成功，返回 `dev task ID` 和 BITS 链接

## 参考

如需看底层参数与示例，参考：

- `@references/usage.md`
