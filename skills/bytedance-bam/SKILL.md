---
name: bytedance-bam
description: "Operate BAM via bytedcli: list/search PSMs, list methods, get method details, query service versions. Use when tasks mention BAM, API management, PSM, or method lookup."
---

# bytedcli BAM

## When to use

- PSM 搜索、收藏、最近查看
- 方法列表 / 方法详情
- 服务版本查询

## 前置条件

- 使用通用调用方式：`references/invocation.md`

> 示例省略 invocation 前缀。

## Quick start

```bash
# PSM 列表
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest bam list-recent-psm --cluster default
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest bam list-starred-psm --cluster default
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest bam search-psm "codebase.app.openapi" --cluster default

# 方法列表 / 详情
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest bam list-method --psm "codebase.app.openapi"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest bam get-method --endpoint-id 2404309 --version 1.0.337
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest bam get-method --psm "codebase.app.openapi" --method "GetRepository"

# 版本历史
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest bam versions "codebase.app.openapi" --cluster default
```

## Notes

- `get-method` 支持 `--endpoint-id` 或 `--psm` + `--method` 两种定位方式
- `--schema ref|raw` 控制 schema 展示方式
- 缺少必填参数会自动输出帮助信息
- 需要结构化输出加 `--json`（全局选项，放在子命令之前，如 `NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest --json bam get-method ...`）

## References

- `references/bam.md`
