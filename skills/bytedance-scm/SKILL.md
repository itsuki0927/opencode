---
name: bytedance-scm
description: "Operate SCM via bytedcli: list starred repos, search repos, list versions, trigger builds, and fetch build logs. Use when tasks mention SCM repositories."
---

# bytedcli SCM

## When to use

- 仓库检索、版本列表、触发构建
- 拉取构建日志

## 前置条件

- 使用通用调用方式：`references/invocation.md`

> 示例省略 invocation 前缀。

## Quick start

```bash
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest scm list-starred-repo --page 1 --size 10
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest scm search-repo "byteapi/command/bytedcli"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest scm list-repo-version "byteapi/command/bytedcli" --branch master --type online --status build_ok
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest scm build-repo "byteapi/command/bytedcli" --branch master --type test -e '{"CUSTOM_KEY":"VALUE"}' -m "trigger build reason"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest scm get-build-log "byteapi/command/bytedcli" "1.0.0.1686" --step building
```

## Notes

- 需要结构化输出加 `--json`（全局选项，放在子命令之前，如 `NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest --json scm list ...`）

## References

- `references/scm.md`
