# Codebase (bytedcli)

```bash
# 配置 PAT
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase config-add-pat <pat>

# 仓库与 MR
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase get-repository --repo-name "byteapi/bytedcli"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase get-merge-request 821 --repo-name "byteapi/bytedcli"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase list-mr-comments --repo-name "byteapi/bytedcli" --mr-iid 821

# Diff / 文件
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase mr-changes --repo-name "byteapi/bytedcli" --mr-iid 821
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase mr-diff 821 --repo-name "byteapi/bytedcli" --file "path/to/file.ts"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase get-file --repo-name "byteapi/bytedcli" --path "README.md" --revision master

# CI / Check Runs
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase list-mr-checks 821 --repo-name "byteapi/bytedcli"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase list-check-runs --repo-name "byteapi/bytedcli" --branch master
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase analyze-mr-ci 821 --repo-name "byteapi/bytedcli"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase get-check-run-step-log 2395465271 unit_test_and_coverage --run-seq 126 --step-id 1259002466

# Issue 评论
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase comment-issue --repo-name "byteapi/bytedcli" --issue-number 24 --content "ack"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase delete-issue --repo-name "byteapi/bytedcli" --issue-number 24

# 创建 MR
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase create-mr --repo-name "byteapi/bytedcli" \
  --source-branch feature/foo --target-branch master --title "feat: demo"

# MR 批量/列表能力
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase batch-get-merge-requests --repo-name "byteapi/bytedcli" --mr-number 821 --mr-number 822
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase list-repo-merge-requests --repo-name "byteapi/bytedcli" --status open --page-size 20
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase get-repo-merge-requests-count --repo-name "byteapi/bytedcli"

# MR 生命周期操作
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase close-merge-request --repo-name "byteapi/bytedcli" --mr-number 821
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase reopen-merge-request --repo-name "byteapi/bytedcli" --mr-number 821
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase merge-merge-request --repo-name "byteapi/bytedcli" --mr-number 821 --merge-method rebase_merge

# MR 合并冲突/绕过策略
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase get-merge-request-mergeability --repo-name "byteapi/bytedcli" --mr-number 821
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase list-merge-request-conflicts --repo-name "byteapi/bytedcli" --mr-number 821
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase list-merge-request-bypasses --repo-name "byteapi/bytedcli" --mr-number 821
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase create-merge-request-bypasses --repo-name "byteapi/bytedcli" --mr-number 821 --inputs-json '[{"kind":"check_run","target":"check_name"}]'

# Review 能力
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase create-review --repo-name "byteapi/bytedcli" --mr-number 821 --status approved --content "LGTM"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase get-review-status --repo-name "byteapi/bytedcli" --mr-number 821
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase list-reviewers --repo-name "byteapi/bytedcli" --mr-number 821
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase update-reviewers --repo-name "byteapi/bytedcli" --mr-number 821 --reviewer-id 123456 --reviewer-id 234567 --set-reviewers true

# Merge Queue 能力
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase get-merge-queue --repo-name "byteapi/bytedcli" --target-branch master
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase list-merge-queue-entries --repo-name "byteapi/bytedcli" --target-branch master --page-size 20
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase enqueue-merge-request --repo-name "byteapi/bytedcli" --mr-number 821 --merge-method rebase_merge
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase dequeue-merge-request --repo-name "byteapi/bytedcli" --mr-number 821

# check_run 读写能力
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase get-check-run --repo-name "byteapi/bytedcli" --id c1
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase create-check-run --repo-name "byteapi/bytedcli" --payload-json '{"Name":"ci/test","CommitId":"<sha>"}'
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase update-check-run --repo-name "byteapi/bytedcli" --payload-json '{"Id":"c1","Status":"completed","Conclusion":"success"}'
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase operate-check-run --repo-name "byteapi/bytedcli" --payload-json '{"Id":"c1","OperationId":"retry"}'
```

## 新增命令清单（merge_request / review / merge_queue）

- `batch-get-merge-requests`
- `batch-update-merge-requests`
- `list-repo-merge-requests`
- `get-repo-merge-requests-count`
- `close-merge-request`
- `reopen-merge-request`
- `merge-merge-request`
- `can-resolve-merge-request-conflicts-in-ui`
- `get-merge-request-mergeability`
- `get-merge-request-setting`
- `list-merge-request-conflicts`
- `get-merge-request-conflict`
- `resolve-merge-request-conflicts`
- `list-merge-request-bypasses`
- `create-merge-request-bypasses`
- `get-check-run`
- `create-check-run`
- `update-check-run`
- `operate-check-run`
- `create-review`
- `get-review-status`
- `list-review-network-statistics`
- `list-reviewers`
- `update-reviewers`
- `get-merge-queue`
- `list-merge-queue-entries`
- `list-merge-request-queue-entries`
- `enqueue-merge-request`
- `dequeue-merge-request`
- `delete-issue`
