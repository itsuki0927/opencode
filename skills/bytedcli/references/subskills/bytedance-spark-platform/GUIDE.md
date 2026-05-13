---
name: bytedance-spark-platform
description: "Operate Spark Platform via bytedcli: list spaces, list/get/create links, summarize deployConfig schema, and manage link env entries. Use when tasks mention Spark Platform (i18n-tt)."
---

# bytedcli Spark Platform

## 如何调用 bytedcli

先选择一种调用方式。下面所有示例默认直接写 `bytedcli`。

```bash
# 方式 1：直接用 npx 运行最新版
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest <command> [options]

# 方式 2：先全局安装，再直接调用 bytedcli
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npm install -g @bytedance-dev/bytedcli@latest
bytedcli <command> [options]
```

## When to use

- Spark Platform space/link 查询
- 想把 link 的 deployConfig 做摘要（解析 schemaUrl、bundle、bundlePath、动态参数、条件摘要）
- 管理 link env（list/set/delete），写操作先 `--dry-run` 预览 payload

## Quick start

```bash
# 查看命令帮助
bytedcli spark-platform --help

# Space
bytedcli spark-platform space list --name "Search" --tag "search"

# Link
bytedcli spark-platform link list --space-id "space_demo" --page 1 --page-size 10
bytedcli spark-platform link get --link-key "demo_link"
bytedcli spark-platform link summary --link-key "demo_link"

# Env
bytedcli spark-platform link env list --link-key "demo_link" --app-id 22
bytedcli spark-platform link env set --link-key "demo_link" --env "ppe_demo" --deploy-config-file ./deploy-config.json --dry-run
bytedcli spark-platform link env delete --link-key "demo_link" --env "ppe_demo" --dry-run
```

## Notes

- Spark Platform 当前固定为 i18n-tt（host: `spark-platform.tiktok-row.net`），无需传 `--site`
- 全局 `--json` 放在 domain 前：`bytedcli --json spark-platform ...`
