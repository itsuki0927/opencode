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

# 创建 MR
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest codebase create-mr --repo-name "byteapi/bytedcli" \
  --source-branch feature/foo --target-branch master --title "feat: demo"
```
