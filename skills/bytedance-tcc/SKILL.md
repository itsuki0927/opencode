---
name: bytedance-tcc
description: "Operate TCC via bytedcli: list/search namespaces, list/get configs, create/update/deploy configs, list directories, import base config, and inspect metadata. Use when tasks mention TCC or config center."
---

# bytedcli TCC

## When to use

- Namespace/Config 查询
- 配置创建、更新、发布（通过 `--publish-mode` 控制发布策略）
- 目录查询与基准配置导入

## 前置条件

- 使用通用调用方式：`references/invocation.md`

> 示例省略 invocation 前缀。

## Quick start

```bash
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest tcc list-sites
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest tcc list-starred-namespace --tcc-site prod --page 1 --size 50
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest tcc search-namespace "keyword" --tcc-site prod --scope all --page 1 --size 50
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest tcc list-config "namespace" --region CN
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest tcc get-config "namespace" "config_name" --region CN --dir "/default"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest tcc list-dir "namespace" --env ppe_xxx --tcc-site i18n-bd
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest tcc list-meta-data --env ppe_xxx --tcc-site i18n-bd
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest tcc create-config "namespace" "config_name" --env ppe --tcc-site prod --region CN --dir "/default" --value "a: b"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest tcc update-config "namespace" "config_name" --env ppe --tcc-site prod --region CN --value "a: b"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest tcc deploy-config "namespace" "config_name" --env ppe --tcc-site prod --region CN
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest tcc import-base-config "namespace" --config-ids "123,456" --target-env ppe_xxx --tcc-site i18n-bd
# Only create deployment, do not start (manual mode)
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest tcc deploy-config "namespace" "config_name" --env ppe --region CN --publish-mode manual
# Deploy with review support (auto mode, default): auto-publish if no review, otherwise return review info
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest tcc deploy-config "namespace" "config_name" --env prod --tcc-site prod --region CN --publish-mode auto
# Force auto-publish regardless of review requirement
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest tcc deploy-config "namespace" "config_name" --env prod --tcc-site prod --region CN --publish-mode force-auto
```

## Notes

- 环境/region/dir 建议显式指定
- 站点 `--tcc-site` 支持：`prod|boe|i18n-bd|i18n-tt|us-ttp|eu-ttp`（别名：`boei18n/boe-i18n/i18n` -> `i18n-bd`）
- 需要结构化输出加 `--json`（全局选项，放在子命令之前，如 `NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest --json tcc list-configs ...`）
- `tcc deploy-config` 通过 `--publish-mode` 控制发布策略：
  - `auto`（默认）：不需要 review 时自动 start/finish；需要 review 时创建审批工单，返回 console URL 和审批人
  - `manual`：只创建发布工单，不自动 start/finish
  - `force-auto`：无论是否需要 review，都自动 start/finish
  - 被 SCP 策略封禁时，返回逃逸申请链接

## References

- `references/tcc.md`
