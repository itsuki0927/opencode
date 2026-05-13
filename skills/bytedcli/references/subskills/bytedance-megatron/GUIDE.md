---
name: bytedance-megatron
description: "Operate Megatron (Spark app management) via bytedcli: get Spark app metadata by application IDs, get queue usage. Use when tasks mention Megatron, Spark apps, Spark app metadata, or queue usage."
---

# bytedcli Megatron

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

- Megatron Spark 应用管理
- 查询 Spark 应用元数据（通过 application ID）
- 查询队列使用情况
- 支持多区域（cn, sg, gcp, va, boe, boei18n）

> 执行前缀见 `references/invocation.md`；下面示例直接写 `bytedcli`。

## Quick start

```bash
# 查询 Spark 应用元数据（单个 ID）
bytedcli megatron app get --app-ids application_1773129958997_436675 --region sg

# 查询 Spark 应用元数据（多个 ID，逗号分隔）
bytedcli megatron app get --app-ids application_1773129958997_436675,application-ee328b5e-1773129958997-384121 --region sg

# 查询 Spark 应用元数据（多个 ID，空格分隔）
bytedcli megatron app get --app-ids application_1773129958997_436675 application-ee328b5e-1773129958997-384121 --region sg

# 查询队列使用情况
bytedcli megatron queue get-usage --queue-name root.common_dw_etl_virtual_p1 --region sg
bytedcli megatron queue get-usage --queue-name root.byodel22_abtest_my_common --region va
```

## Supported Regions

| Region | Description | API Endpoint |
|--------|-------------|--------------|
| `cn` | China (default) | https://bc-cn-gw.bytedance.net |
| `sg` | Singapore | https://bc-sg-gw.tiktok-row.net |
| `gcp` | EU | https://bc-iedt-gw.tiktok-eu.net |
| `va` | US East (Virginia) | https://bc-maliva-gw.tiktok-row.net |
| `boe` | BOE (CN) | https://bc-boe-gw.bytedance.net |
| `boei18n` | BOE (International) | https://bc-boe-gw.bytedance.net |

## Notes

- 需要结构化输出加 `--json`
- `--app-ids` 支持逗号分隔或空格分隔的 application ID
- `--region` 可选，默认为 `cn`

## References

- `references/megatron.md`
- `references/invocation.md`
- `references/troubleshooting.md`
