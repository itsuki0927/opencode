---
name: bytedance-aeolus
description: "Query and explore Aeolus BI/data analytics platform via bytedcli: list authorized datasets and dashboards, get dataset field details (dimensions and metrics), get dataset model info (underlying data source and query), execute SQL queries, and manage Query Editor files/folders for ad-hoc SQL execution (Hive or ClickHouse via --engine ch). Use when tasks mention Aeolus, BI dashboards, datasets, data analytics queries, or Query Editor."
---

# bytedcli Aeolus (Data Analytics Platform)

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

- List dashboards and datasets you have access to
- Get dataset field details (dimensions and metrics)
- Get dataset model info (underlying data source, query, and table schema)
- Execute SQL queries against datasets
- Explore Aeolus BI platform data
- Manage Query Editor folders and query files (CRUD)
- Run ad-hoc SQL queries via Query Editor (Hive runner by default, or ClickHouse when SQL matches the browser Query Editor CH task, e.g. `params{'...'}`)

## 前置条件

- 使用通用调用方式：`references/invocation.md`

> 执行前缀见 `references/invocation.md`；下面示例直接写 `bytedcli`。

## Supported Regions

Dataset / report API 默认域名与 `src/api/aeolus/site.ts` 一致；控制台入口可能因租户不同而异。

| Region | Description | Default API host |
|--------|-------------|------------------|
| `cn` | China | `https://data.bytedance.net` |
| `sg` | Singapore (TikTok row) | `https://aeolus-sg.tiktok-row.net` |
| `va` | US East (TikTok row) | `https://aeolus-va.tiktok-row.net` |
| `mycis` | MYCIS | `https://aeolus-mycis.byteintl.net` |
| `mybd` | MYBD | `https://aeolus-mybd.sinf.net` |
| `sglark` | Singapore Lark | `https://aeolus-sglark.bytedance.net` |
| `usttpusts` | US TTP USTS | `https://aeolus-tx.tiktok-usts.net` |

## Quick start

For report/dataQuery URLs, prefer this workflow by default:

1. `resolve-report` to get the dataset ID.
2. `dataset-fields` to confirm dimensions/metrics and partition fields.
3. `dataset-model-info` to inspect the underlying query and lineage.
4. If logical dataset SQL fails or only returns `dummy`, inspect `system.query_log` to locate the backing physical `aeolus_data_db_*`.`aeolus_data_table_*`.
5. Query the physical table directly.

```bash
# List authorized datasets and dashboards (region is required)
bytedcli aeolus list-authorized -r va --limit 20

# Filter by type (dashboard or data_set)
bytedcli aeolus list-authorized -r cn --type data_set

# Resolve a dataQuery/report URL to dataset IDs before querying
bytedcli aeolus resolve-report -r va --url "https://aeolus-va..."

# Get dataset field details (dimensions and metrics)
bytedcli aeolus dataset-fields -r va 1576311

# Get dataset model info (underlying query, lineage, source table / physical table hints)
bytedcli aeolus dataset-model-info -r va --app-id 1000252 --dataset-id 2109028

# If direct logical SQL fails, inspect query_log to find the actual physical table name
bytedcli aeolus query -r va 1576311 "SELECT event_time, query FROM system.query_log WHERE query LIKE '%aeolus_data_table_%' ORDER BY event_time DESC LIMIT 20"

# Query the physical Aeolus table directly after locating it
bytedcli aeolus query -r va 1576311 "SELECT reporting_ad_id, max(pangle_rolling3d_dollar_cost) AS pangle_rolling3d_dollar_cost FROM \`aeolus_data_db_xxx\`.\`aeolus_data_table_xxx\` WHERE p_date = '2026-03-01' GROUP BY reporting_ad_id ORDER BY pangle_rolling3d_dollar_cost DESC LIMIT 10"
```

## Recommended workflow for report/dataQuery links

1. Use `resolve-report` to get the dataset ID from the report URL.
2. Use `dataset-fields` to confirm dimensions/metrics and identify partition fields.
3. Always use `dataset-model-info` before assuming logical dataset SQL will work. Many Aeolus datasets expose derived fields in metadata, but `aeolus query` may only succeed against the backing physical ClickHouse table, not a logical dataset alias like `[DatasetName]` or `"2231500"`.
4. If direct logical dataset SQL fails with errors like `unknownTable`, `unknownIdentifier`, or only returns `dummy`, inspect:
   - `modelInfo.nodeConf[].query` for the source logic
   - `modelInfo.nodeConf[].lineageInfo` for upstream tables
   - `system.query_log` via `aeolus query` to find the real physical table name used by Aeolus (often `aeolus_data_db_*`.`aeolus_data_table_*`)
5. Query the physical Aeolus table directly, and deduplicate with `GROUP BY` / `max(...)` when repeated rows exist per key.
6. Do not stop at `SELECT * LIMIT 1` returning only `dummy`; that usually means you still need the physical table, not that the dataset is unusable.

### Failure signatures

- `unknownTable` when using a logical dataset name or dataset ID as the table
- `unknownIdentifier` / missing field errors even though the field exists in `dataset-fields`
- `SELECT * LIMIT 1` or `select dummy` only returning a `dummy` column

These are all strong signals to switch from logical dataset SQL to physical-table discovery.

### End-to-end fallback example

```bash
# 1) Resolve the report URL
bytedcli aeolus resolve-report -r va --url "https://aeolus-va..."

# 2) Inspect semantic fields and partition fields
bytedcli aeolus dataset-fields -r va 2231500

# 3) Inspect the underlying model/query
bytedcli aeolus dataset-model-info -r va --app-id 555116 --dataset-id 2231500

# 4) Find the backing physical table from recent Aeolus queries
bytedcli aeolus query -r va 2231500 "SELECT event_time, query FROM system.query_log WHERE query LIKE '%aeolus_data_table_%' ORDER BY event_time DESC LIMIT 50"

# 5) Query the physical table directly
bytedcli aeolus query -r va 2231500 "SELECT reporting_ad_id, sum(placement_dollar_cost_1d/100000) AS cost FROM \`aeolus_data_db_xxx\`.\`aeolus_data_table_xxx\` WHERE p_date = '2026-04-07' AND placement = 'Pangle' GROUP BY reporting_ad_id ORDER BY cost DESC LIMIT 5"
```

## SQL Syntax Notes

- Do **not** assume ``FROM `[DatasetName]` `` or ``FROM "<datasetId>"`` will work. For many datasets this returns `unknownTable`.
- `dataset-fields` lists semantic fields, but not every field name can be queried directly without first locating the physical Aeolus table.
- If `SELECT * LIMIT 1` returns only `dummy`, that does **not** prove the dataset is unusable; it usually means you are not yet querying the backing table.
- Prefer physical-table SQL once you have identified the actual table name from `system.query_log` or dataset model info.
- Partition fields must still be included in `WHERE` clauses where applicable.

## Authentication

By default, Aeolus commands reuse the token obtained from `bytedcli auth login`, just like most other bytedcli domains.

For most Dataset API commands, you can optionally configure region-specific `ClientID/ClientSecret` in `.aeolus.env` or environment variables. When present, CLI will prefer those credentials, which is useful for automation:

1. Visit the Aeolus Developer Console to get your ClientID and ClientSecret（域名以租户为准，常见如下）:
   - **CN region**: [data.bytedance.net](https://data.bytedance.net/aeolus/pages/developer/console/certification)
   - **SG region**: [aeolus-sg.tiktok-row.net](https://aeolus-sg.tiktok-row.net/pages/developer/console/certification)
   - **VA region**: [aeolus-va.tiktok-row.net](https://aeolus-va.tiktok-row.net/pages/developer/console/certification)
2. Create `.aeolus.env` file (choose one location):
   - **Global**: `~/.bytedcli/.aeolus.env` (recommended for npm global install)
   - **Local**: `./.aeolus.env` in current working directory (overrides global)

```bash
# Region-specific credentials
BYTEDCLI_AEOLUS_CN_CLIENT_ID=your_cn_client_id
BYTEDCLI_AEOLUS_CN_CLIENT_SECRET=your_cn_client_secret
BYTEDCLI_AEOLUS_SG_CLIENT_ID=your_sg_client_id
BYTEDCLI_AEOLUS_SG_CLIENT_SECRET=your_sg_client_secret
BYTEDCLI_AEOLUS_VA_CLIENT_ID=your_va_client_id
BYTEDCLI_AEOLUS_VA_CLIENT_SECRET=your_va_client_secret
```

## Query Editor (ad-hoc SQL)

Query Editor defaults to the authentication result obtained from `bytedcli auth login`, but it does not support region-specific `ClientID/ClientSecret` overrides. It defaults to `cn`, and also supports `-r/--region` to switch between `cn`, `sg`, `va`, `mycis`, `mybd`, `sglark`, and `usttpusts`. For `mycis` and `mybd`, Query Editor reuses the local browser session for `i18n-bd`. For `usttpusts`, it reuses the local browser session for `us-ttp-usts`.

### Authentication

```bash
# One-time login
bytedcli auth login

# Query Editor on mycis / mybd
bytedcli --site i18n-bd auth login --session
```

Cookies are cached locally and reused until expiry (~14 days). For `mycis` and `mybd`, make sure the `i18n-bd` browser session is ready first. For `usttpusts`, make sure the `us-ttp-usts` browser session is ready first.

### Quick start

```bash
# Check current user
bytedcli aeolus query-editor whoami
bytedcli aeolus query-editor whoami --region sg

# Folder management
bytedcli aeolus query-editor folder list
bytedcli aeolus query-editor folder list --region va
bytedcli aeolus query-editor folder tree
bytedcli aeolus query-editor folder create --name "my-queries"

# File management
bytedcli aeolus query-editor file create --name "test" --folder-id 123
bytedcli aeolus query-editor file write-sql --file-id 456 --sql "SELECT 1"
bytedcli aeolus query-editor file search --keyword "test"

# SQL execution
bytedcli aeolus query-editor query run --file-id 456 --folder-id 123 --sql "SELECT 1"
bytedcli aeolus query-editor query run --file-id 456 --folder-id 123 --file ./queries/demo.sql
bytedcli aeolus query-editor query status --task-id 789 --file-id 456 --folder-id 123
bytedcli aeolus query-editor query logs --task-id 789

# One-shot query (auto-creates file, runs SQL, returns results)
bytedcli aeolus query-editor query one --sql "SELECT 1"
```

### Query Editor: ClickHouse (`--engine ch`)

默认走 Hive `/hive/task/run`；与浏览器 Query Editor 一致的 ClickHouse 任务请用 **`--engine ch`**（`/ch/task/*`）、并保证 **`status` / `logs` 与 `run` 使用相同 `--engine`**。参数表、`QE_APP_ID`、`BYTEDCLI_CLOUD_SITE`（VA/SG 常为 `i18n-tt`）等完整说明见 **`references/aeolus.md` 的「Query Editor」章节**。

### Recommended usage: `query one` vs full Query Editor workflow

- Use `aeolus query-editor query one` for one-off or exploratory SQL where you only need to run a small number of temporary queries quickly.
- Use the full Query Editor workflow when you are analyzing one system or topic and expect multiple related SQL queries over time.
- The full workflow avoids creating a new temporary folder on every query, lets you reuse the same folder/file IDs, and keeps related SQL under one theme directory so you can search and review query history later.
- In the full workflow, prefer passing SQL directly to `query run --sql ...` or `query run --file ...`. Writing SQL into the file first is optional, not required for execution.
- Under the hood, both `query run --sql ...` and `query run --file ...` call the same Query Editor `run` API with the same `page_id` / `block_id`; **Hive** (default) sends `yarn` queue fields, while **`--engine ch`** sends `cluster_name` / `region` instead. The only difference between `--sql` and `--file` is where `query` / `query_template` text comes from.
- A practical organization pattern is: create one folder for the overall analysis theme, create multiple files for different sub-scenarios under that theme, and then reuse the same `file-id` for multiple `query run` executions when one sub-scenario needs several SQL variants.
- In that model, `folder-id` is the theme container, and `file-id` is closer to a reusable query context for one sub-scenario than a hard binding to exactly one SQL statement.

Recommended persistent workflow:

```bash
# 1) Create or reuse a theme folder once
bytedcli aeolus query-editor folder create --name "svc-frk-analysis"

# 2) Create one or more query files inside that folder
bytedcli aeolus query-editor file create --name "partitions" --folder-id 123
bytedcli aeolus query-editor file create --name "daily-sample" --folder-id 123
bytedcli aeolus query-editor file create --name "rootcause-drilldown" --folder-id 123

# 3) Run queries against the same reusable file/folder IDs
bytedcli aeolus query-editor query run --file-id 456 --folder-id 123 --sql "SHOW PARTITIONS svc_frk.ods_cp_cds_keys_df"
bytedcli aeolus query-editor query run --file-id 457 --folder-id 123 --sql "SELECT * FROM svc_frk.ods_cp_cds_keys_df WHERE date = '20260412' LIMIT 100"
bytedcli aeolus query-editor query run --file-id 457 --folder-id 123 --file ./queries/daily-sample.sql
bytedcli aeolus query-editor query run --file-id 458 --folder-id 123 --sql "SELECT protocol, date FROM svc_frk.ods_cp_cds_keys_usttp_df WHERE date = '20260412' LIMIT 10"
bytedcli aeolus query-editor query run --file-id 458 --folder-id 123 --sql "SELECT to_service, count(*) FROM svc_frk.ods_cp_cds_keys_usttp_df WHERE date = '20260412' GROUP BY to_service LIMIT 20"

# 4) Optionally persist SQL into the file body for later viewing/editing in Query Editor UI
bytedcli aeolus query-editor file write-sql --file-id 456 --sql "SHOW PARTITIONS svc_frk.ods_cp_cds_keys_df"
bytedcli aeolus query-editor file write-sql --file-id 457 --sql "SELECT * FROM svc_frk.ods_cp_cds_keys_df WHERE date = '20260412' LIMIT 100"

# 5) Inspect task status / logs and search historical SQL files later
bytedcli aeolus query-editor query status --task-id 789 --file-id 456 --folder-id 123
bytedcli aeolus query-editor query logs --task-id 789
bytedcli aeolus query-editor file search --keyword "svc_frk"
```

Notes:

- `query one` is optimized for convenience, not long-term organization.
- `query run` should include `--sql` or `--file` when you want to execute against an existing `file-id` / `folder-id`.
- For repeated analysis, prefer naming folders by topic/system (for example `svc-frk-analysis`, `creator-growth-debug`, `dashboard-245033-rootcause`).
- Query Editor commands default to `cn`, and support `-r/--region` to switch host/domain consistently with Aeolus dataset/report APIs.

### Command structure

```
aeolus query-editor
  ├── whoami / queues / datasources
  ├── folder  list|tree|create|rename|move|delete
  ├── file    get|create|write-sql|rename|move|delete|search
  └── query   run|status|logs|one
```

## Notes

- Use `--json` for structured JSON output (global option before subcommand)
- **Region (`-r`) is required** for all Dataset API commands
- Dataset ID can be found in `list-authorized` output
- App ID can be found in `list-authorized` JSON output (`app.id` field)
- Partition fields are marked in `dataset-fields` output
- `dataset-fields`, `dataset-model-info` and `query` only work with `data_set` type, not `dashboard`
- Query Editor commands default to `cn`; pass `-r/--region <region>` to target `sg`, `va`, `mycis`, `mybd`, `sglark`, or `usttpusts`

## References

- `references/aeolus.md`（命令级参考；含 **Query Editor**、`--engine ch`、Regions 与鉴权）
- `references/invocation.md`
