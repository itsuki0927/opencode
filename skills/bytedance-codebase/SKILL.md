---
name: bytedance-codebase
description: "Operate Codebase: repositories, merge requests, diffs, files, check runs, and CI analysis."
---

# Codebase（bytedcli）

## When to use

- 仓库查询、MR 详情/评论
- Diff 列表/内容、文件查看
- Check Runs 与 CI 失败分析
- 创建 Merge Request

## 前置条件

- 使用通用调用方式：`references/invocation.md`
- 需要配置 PAT：`NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase config-add-pat <pat>`

> 示例省略 invocation 前缀。

## Quick start

```bash
# 仓库
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase get-repository --repo-name "byteapi/bytedcli"

# MR 详情/评论
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase get-merge-request 821 --repo-name "byteapi/bytedcli"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase list-mr-comments --repo-name "byteapi/bytedcli" --mr-iid 821

# Diff 文件/内容
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase mr-changes --repo-name "byteapi/bytedcli" --mr-iid 821
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase mr-diff 821 --repo-name "byteapi/bytedcli" --file "path/to/file.ts"

# 文件内容
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase get-file --repo-name "byteapi/bytedcli" --path "README.md" --revision master

# 创建 MR
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase create-mr --repo-name "byteapi/bytedcli" --source-branch feature/foo --target-branch master --title "feat: demo"

# Check Runs / CI
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase list-mr-checks 821 --repo-name "byteapi/bytedcli"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase list-check-runs --repo-name "byteapi/bytedcli" --branch master
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase analyze-mr-ci 821 --repo-name "byteapi/bytedcli"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase get-check-run-step-log 2395465271 unit_test_and_coverage --run-seq 126 --step-id 1259002466

# Issue 评论
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase comment-issue --repo-name "byteapi/bytedcli" --issue-number 24 --content "ack"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase delete-issue --repo-name "byteapi/bytedcli" --issue-number 24

# merge_request scope（新增）
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase list-repo-merge-requests --repo-name "byteapi/bytedcli" --status open --page-size 20
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase get-repo-merge-requests-count --repo-name "byteapi/bytedcli"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase close-merge-request --repo-name "byteapi/bytedcli" --mr-number 821
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase get-merge-request-mergeability --repo-name "byteapi/bytedcli" --mr-number 821

# review scope（新增）
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase create-review --repo-name "byteapi/bytedcli" --mr-number 821 --status approved --content "LGTM"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase get-review-status --repo-name "byteapi/bytedcli" --mr-number 821
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase update-reviewers --repo-name "byteapi/bytedcli" --mr-number 821 --reviewer-id 123456 --reviewer-id 234567 --set-reviewers true

# merge_queue scope（新增）
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase get-merge-queue --repo-name "byteapi/bytedcli" --target-branch master
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase list-merge-queue-entries --repo-name "byteapi/bytedcli" --target-branch master --page-size 20
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase enqueue-merge-request --repo-name "byteapi/bytedcli" --mr-number 821 --merge-method rebase_merge

# check_run scope（新增）
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase get-check-run --repo-name "byteapi/bytedcli" --id c1
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase create-check-run --repo-name "byteapi/bytedcli" --payload-json '{"Name":"ci/test","CommitId":"<sha>"}'
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase update-check-run --repo-name "byteapi/bytedcli" --payload-json '{"Id":"c1","Status":"completed","Conclusion":"success"}'
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase operate-check-run --repo-name "byteapi/bytedcli" --payload-json '{"Id":"c1","OperationId":"retry"}'
```

## Notes

- `--repo-name` 与 `--repo-id` 二选一
- 缺少必填参数会输出完整帮助
- 需要结构化输出加 `--json`（全局选项，放在子命令之前，如 `NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest --json codebase get-merge-request ...`）
- 新增 scope 命令较多，完整列表见 `references/codebase.md` 的“新增命令清单”

## References

- `references/codebase.md`
