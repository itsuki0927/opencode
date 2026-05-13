# Megatron CLI Reference

Megatron 是 Spark 应用管理平台，提供 Spark 应用元数据查询和队列使用情况查询功能。

Supported built-in regions: `cn`, `sg`, `gcp`, `va`, `boe`, `boei18n`.

## Commands

### app get

查询 Spark 应用元数据。

```bash
bytedcli megatron app get [options]
```

**Options:**
- `--app-ids <appIds...>` - Application IDs (comma-separated or space-separated) (required)
- `--region <region>` - Region (cn, sg, gcp, va, boe, boei18n) (default: "cn")

**Examples:**
```bash
# 单个 ID
bytedcli megatron app get --app-ids application_1773129958997_436675 --region sg

# 多个 ID，逗号分隔
bytedcli megatron app get --app-ids application_1773129958997_436675,application-ee328b5e-1773129958997-384121 --region sg

# 多个 ID，空格分隔
bytedcli megatron app get --app-ids application_1773129958997_436675 application-ee328b5e-1773129958997-384121 --region sg
```

---

### queue get-usage

查询队列使用情况。

```bash
bytedcli megatron queue get-usage [options]
```

**Options:**
- `--queue-name <queueName>` - Queue name (required)
- `--region <region>` - Region (cn, sg, gcp, va, boe, boei18n) (default: "cn")

**Examples:**
```bash
# 查询队列使用情况
bytedcli megatron queue get-usage --queue-name root.common_dw_etl_virtual_p1 --region sg
bytedcli megatron queue get-usage --queue-name root.byodel22_abtest_my_common --region va
```

## Authentication

The CLI uses JWT authentication via SSO. Ensure you are logged in:

```bash
bytedcli auth login
```
