---
name: bytedance-codebase
description: "Operate Codebase: repositories, merge requests, diffs, files, check runs, CI analysis, and dependency permissions."
---

# Codebase（bytedcli）

## 如何调用 bytedcli

先选择一种调用方式。下面所有示例默认直接写 `bytedcli`。

```bash
# 方式 1：直接用 npx 运行最新版
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest <command> [options]

# 方式 2：先全局安装，再直接调用 bytedcli
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npm install -g @bytedance-dev/bytedcli@latest
bytedcli <command> [options]
```

- 使用 `npx` 时，把后文示例里的 `bytedcli` 替换成 `NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest`
- 已全局安装时，直接按后文示例执行 `bytedcli ...`

## When to use

- 仓库查询、MR 详情/评论
- Diff 列表/内容、文件查看
- Check Runs 与 CI 失败分析
- 聚合 MR 状态与跨仓库搜索
- 创建分支
- 创建 Merge Request
- MR 关联 Meego 工作项（需求/缺陷）
- 依赖权限检查与批量申请

## 前置条件

- 使用通用调用方式：`references/invocation.md`
- 认证优先级：本地 `codebase_auth.json` JWT > `BYTEDCLI_USER_CODE_JWT` > `AIME_USER_CODE_JWT` > PAT。需要手动配置 PAT 时使用：`bytedcli codebase auth config-add-pat <pat>`

> 执行前缀见 `references/invocation.md`；下面示例直接写 `bytedcli`。

## Quick start

```bash
# 仓库
bytedcli codebase repo get "example-org/example-repo"

# MR 详情/评论
bytedcli codebase mr get 821 -R "example-org/example-repo"
bytedcli codebase mr comment list 821 -R "example-org/example-repo"

# Diff 文件/内容
bytedcli codebase mr files 821 -R "example-org/example-repo"
bytedcli codebase mr diff 821 -R "example-org/example-repo" --file "path/to/file.ts"

# 文件内容
bytedcli codebase repo file "README.md" -R "example-org/example-repo"

# 创建 Branch
bytedcli codebase repo branch create feat/demo -R "example-org/example-repo" --from master

# 管理 Tag
bytedcli codebase repo tag list -R "example-org/example-repo" --query "v1." --query-mode prefix
bytedcli codebase repo tag get -R "example-org/example-repo" --name v1.0.0
bytedcli codebase repo tag create -R "example-org/example-repo" --name v1.0.1 --revision master --message "Release v1.0.1"
bytedcli codebase repo tag delete -R "example-org/example-repo" --name v1.0.1

# 管理 Release
bytedcli codebase release list -R "example-org/example-repo" --query "v1." --query-mode prefix
bytedcli codebase release get -R "example-org/example-repo" --tag v1.0.0
bytedcli codebase release create -R "example-org/example-repo" --tag v1.0.1 --description "Release v1.0.1" --revision master --tag-message "Release v1.0.1"
bytedcli codebase release update -R "example-org/example-repo" --tag v1.0.1 --description "Updated release notes"

# 创建 MR
bytedcli codebase mr create -R "example-org/example-repo" --title "feat: demo"
bytedcli codebase mr create -R "example-org/example-repo" --title "feat: demo" --meego 7074189149

# 更新 MR：关联工作项 / 切 target branch
bytedcli codebase mr update 821 -R "example-org/example-repo" --meego 7074189149
bytedcli codebase mr update 821 -R "example-org/example-repo" --base develop

# Check Runs / CI
bytedcli codebase checks mr 821 -R "example-org/example-repo"
bytedcli codebase checks list -R "example-org/example-repo"
bytedcli codebase checks list -R "example-org/example-repo" --commit <sha> --mr 821
bytedcli codebase checks mr --mr "https://code.byted.org/example-org/example-repo/merge_requests/821" -R "example-org/example-repo"
bytedcli codebase checks get -R "example-org/example-repo" --id c1
bytedcli codebase checks log 2395465271 unit_test_and_coverage --run-seq 126 --step-id 1259002466
bytedcli codebase checks log 2552744121 build_lint-step_4 --run-seq 1 --no-limit
bytedcli codebase checks log --url "https://bits.bytedance.net/p/job_runs/2395465271/step_logs/unit_test_and_coverage?runSeq=126&stepId=1259002466"
bytedcli codebase checks log -R "example-org/example-repo" --check-run-id 765416657961248
bytedcli codebase checks log -R "example-org/example-repo" --check-run-id 765416657961248 > /tmp/check.log
grep -n 'error\\|fail' /tmp/check.log
bytedcli codebase mr status 821 -R "example-org/example-repo"

# Issue
bytedcli codebase issue comment 24 -R "example-org/example-repo" --body "ack"
bytedcli codebase issue delete 24 -R "example-org/example-repo"
bytedcli codebase search issue --assignee @me --status todo --page-size 5

# 依赖权限
bytedcli codebase permission check -R "example-org/example-repo"
bytedcli codebase permission check -R "example-org/example-repo" --revision main
bytedcli codebase permission apply -R "example-org/example-repo" --action reporter --reason "need read access" --repos "dep-org/dep-repo"

# MR 列表 / 生命周期
bytedcli codebase mr list -R "example-org/example-repo" --state open -L 20
bytedcli codebase mr count -R "example-org/example-repo"
bytedcli codebase mr close 821 -R "example-org/example-repo"
bytedcli codebase mr status 821 -R "example-org/example-repo"

# review scope（新增）
bytedcli codebase mr review 821 -R "example-org/example-repo" --approve --body "LGTM"
bytedcli codebase mr reviewer list 821 -R "example-org/example-repo"
bytedcli codebase mr reviewer update 821 -R "example-org/example-repo" --set 123456 --set 234567
bytedcli codebase mr reviewer update 821 -R "example-org/example-repo" --set alice --add bob   # 支持 username

# merge_queue scope（新增）
bytedcli codebase mr queue status -R "example-org/example-repo"
bytedcli codebase mr queue list -R "example-org/example-repo" -L 20
bytedcli codebase mr queue enqueue 821 -R "example-org/example-repo" --merge-method rebase_merge
bytedcli codebase search mr --author @me --status open --page-size 5

# check_run scope（新增）
bytedcli codebase checks get -R "example-org/example-repo" --id c1
bytedcli codebase checks create -R "example-org/example-repo" --payload-json '{"Name":"ci/test","CommitId":"<sha>"}'
bytedcli codebase checks update -R "example-org/example-repo" --payload-json '{"Id":"c1","Status":"completed","Conclusion":"success"}'
bytedcli codebase checks operate -R "example-org/example-repo" --payload-json '{"Id":"c1","OperationId":"retry"}'
```

## Notes

- Verb renames: `view` is now `get`, `edit` is now `update`; old names still work as hidden aliases
- `--repo-name` 与 `--repo-id` 二选一
- 在 `code.byted.org` 或 `code-tx.byted.org` 的 Git 仓库目录内，支持仓库选择器的 Codebase 命令可省略 `-R/--repo` 或 `--repo-name`，CLI 会从当前 `origin` 自动推断仓库；如果推断失败，会继续说明当前目录是否不是 Git 仓库、缺少 `origin`、host 不支持，或 remote URL 无法解析
- 分组后的 `codebase repo/commit/mr/issue/checks` 命令以 `-R, --repo` 作为主仓库选择器，同时继续接受隐藏兼容参数 `--repo-name`
- `codebase repo tag list|get|create|delete` 用于查询、创建和删除仓库 Git tag
- `codebase release list|get|create|update` 用于查询和维护挂在 tag 上的 release 描述；其中 `release list` 会按 tag 扫描并解析 release，tag 很多时会更慢
- `codebase commit list|get` 用于查看仓库 commit 历史；未显式传 `--revision` 时会优先使用当前 Git 分支，失败后回落到仓库默认分支
- 在 `code.byted.org` 或 `code-tx.byted.org` 的 Git 仓库目录内，`codebase checks list` / `list-check-runs` 未显式传 `--branch` / `--commit` 时会自动使用当前 Git 分支，并在能解析出对应 MR 时额外分组展示 MR checks；按 commit 查询时可显式传 `--mr` / `--mr-id` 追加 MR 级检查；`codebase mr create` / `create-mr` 未显式传 `--head` / `--source-branch` 时也会自动使用当前 Git 分支
- `codebase mr list` 默认只返回 open；`codebase issue list` 默认只返回未完成态（`backlog/todo/in_progress`），并支持 `--status open|closed|all`
- `codebase mr status` 会聚合 mergeability、review 与 check runs；`codebase search mr` / `codebase search issue` 用于跨仓库搜索，支持 `@me`、仓库路径、标题/关键字、状态等用户视角筛选
- `codebase mr get` / `codebase mr review` / `codebase mr reviewer list|update` / `codebase mr bypass list|create` / `codebase mr queue entries|enqueue|dequeue` 支持 `<number> | <url> | <branch>`，未传 selector 时会默认回落到当前 Git 分支；`codebase issue get` 支持 `<number> | <url>`
- `codebase mr review` 在按 MR selector 创建 review 时会自动附带当前 MR 最新 `source commit`，让 approve/disapprove 计入当前 MR version；如需固定到特定 commit，可显式传 `--commit-id`
- MR 评论入口统一走 `codebase mr comment ...`；常用 thread 动作使用 `codebase mr comment reply|resolve|unresolve`
- MR 级检查入口使用 `codebase checks mr`；公开的 check run 入口使用 `codebase checks list/get/log`；`checks log` 既支持 `<job_run_id> <step_name|step_uid>`，也支持 `--url` 和 `--check-run-id` / `--check-run-external-id` 自动展开日志；只兼容 master 上已有的平铺命令（如 `list-check-runs` / `get-check-run`），不保留 `codebase ci` / `codebase check`
- 排查 MR CI 时，优先走 `codebase checks mr -> codebase checks get -> codebase checks log --check-run-id` 这条链路；先用结构化输出缩小到失败 check / step，再拉日志，不要一开始就盲查全文
- `codebase checks log --check-run-id` 适合作为默认日志入口；它会按整条 check run 批量展开所有可解析日志。日志通常很大，优先重定向到文件，再用 `rg` / `grep` / `less` 搜索，不要直接把整段日志塞进上下文
- 遇到 CI 失败时，先区分是 MR 级 checks、branch / commit 级 check runs，还是 CLI 自己的本地测试回归；不要默认把失败归因到外部平台
- 修完 CI 相关问题后，建议按“定向测试 -> 项目实际构建命令 -> 项目实际全量测试命令 -> 真实命令 smoke check -> `git diff --check`”的顺序验证
- 缺少必填参数会输出完整帮助
- 需要结构化输出加 `--json`（全局选项，放在子命令之前，如 `bytedcli --json codebase get-merge-request ...`）
- 如果运行环境已经注入 `BYTEDCLI_USER_CODE_JWT` 或 `AIME_USER_CODE_JWT`，无需额外执行 `codebase auth config-auth`
- 新增 scope / search 命令较多，完整列表见 `references/codebase.md`
- 遇到 CI / checks 排障时，优先查看 `references/troubleshooting.md` 的通用流程；重点先区分 branch / commit 级 check runs 与 MR 级 checks，再决定是否下钻 step log
- **MR 关联 Meego 工作项工作流**：当用户要在 MR 里关联需求或缺陷时，按以下步骤操作：
  1. **搜索**：用 `bytedcli --json meego workitem list --project-key <project_key> --mql "SELECT \`work_item_id\`, \`name\` FROM \`<project_key>\`.\`story\` WHERE \`name\` LIKE '%关键字%' LIMIT 10"` 按关键字搜索（`story` 为需求，`issue` 为缺陷）
  2. **呈现**：解析 JSON 结果，提取 `work_item_id`（long_value）和 `name`（string_value），以表格形式展示给用户
     - 仅 1 条 → 向用户确认后直接使用
     - 多条 → 展示 ID + 名称列表，让用户选择
     - 0 条 → 提示用户换关键字重试
  3. **执行**：`bytedcli codebase mr create/update --meego <选中的 work_item_id 或 Meego URL>`
- **MR 评论数据结构**：Thread 用 `.Positions`（复数/数组），Comment 用 `.Position`（单数/对象）
- `codebase permission check -R <repo>` 查询仓库依赖中缺少权限的仓库（`level=limited && permission=""`）；`codebase permission apply -R <repo> --action <reporter|developer|master> --reason <text> --repos <repos>` 批量提交权限申请，返回审批链接（`https://kani-cn.bytedance.net/approval/{id}#`）

## References

- `references/codebase.md`
- `references/troubleshooting.md`
