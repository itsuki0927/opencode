# Aeolus CLI Reference

The Aeolus CLI provides commands to interact with the Aeolus BI/data analytics platform, including listing datasets, viewing field details, and executing SQL queries.

## Commands

### list-authorized

List dashboards and datasets you have access to.

```bash
bytedcli aeolus list-authorized [options]
```

**Options:**
- `-r, --region <region>` - Region: cn, sg, va, mycis, mybd, sglark, usttpusts (required)
- `-t, --type <type>` - Filter by type: dashboard, data_set
- `--limit <limit>` - Number of results (default: 20)
- `--offset <offset>` - Pagination offset (default: 0)

**Examples:**
```bash
# List all authorized resources (VA region)
bytedcli aeolus list-authorized -r va

# List only datasets (CN region)
bytedcli aeolus list-authorized -r cn --type data_set --limit 50

# Pagination (SG region)
bytedcli aeolus list-authorized -r sg --offset 20 --limit 20
```

**Output:**
- ID, Type, Name, Owner, App, Last Visit Time

---

### resolve-report

Resolve report and dataset references from Aeolus URLs.

```bash
bytedcli aeolus resolve-report [options]
```

**Options:**
- `-r, --region <region>` - Region: cn, sg, va, mycis, mybd, sglark, usttpusts (required when URL cannot infer region)
- `--url <aeolusUrl>` - Aeolus URL (`dataQuery` or `dashboard`)
- `--app-id <appId>` - App ID (when not using URL)
- `--report-id <reportId>` - Report ID (when not using URL)
- `--json` is a global option and must appear before `aeolus`

**Examples:**
```bash
# Resolve from dataQuery URL
bytedcli aeolus resolve-report --url "https://example.aeolus.net/aeolus/pages/dataQuery?appId=1005563&rid=13958206&sid=4961129"

# Resolve from dashboard URL
bytedcli aeolus resolve-report --url "https://example.aeolus-va.net/pages/dashboard/245033?appId=555175&sheetId=721183"

# Resolve from dashboard URL without sheetId (falls back to current/default sheet)
bytedcli aeolus resolve-report --url "https://example.aeolus-va.net/pages/dashboard/245033?appId=555175"
```

**Output:**
- `dataQuery` URL: report IDs and resolved dataset IDs
- `dashboard` URL: report IDs, resolved dataset IDs, plus
  - `dashboardName`, `dashboardOwnerEmailPrefix`, `dashboardRoleList[]`
  - `sheets[]`: `sheetId`, `name`, `sheetOrder`, `visible`, `reportIds`
  - `reports[]`: `reportId`, `name`, `displayType`, `ownerEmailPrefix`, `statusCode`, `updatedAt`, `datasetIds`

---

### dataset-fields

Get dataset dimensions and metrics (field details).

```bash
bytedcli aeolus dataset-fields <datasetId> [options]
```

**Arguments:**
- `datasetId` - Dataset ID (from list-authorized output)

**Options:**
- `-r, --region <region>` - Region: cn, sg, va, mycis, mybd, sglark, usttpusts (required)
- `--json` is a global option and must appear before `aeolus`

**Examples:**
```bash
# Get dataset fields (VA region)
bytedcli aeolus dataset-fields -r va 1576311

# Get dataset fields (CN region, JSON output)
bytedcli --json aeolus dataset-fields -r cn 185503
```

**Output:**
- Dataset name
- **Dimensions**: ID, Name, Type, Partition flag, Description
- **Metrics**: ID, Name, Type, Expression, Description

---

### dataset-model-info

Get dataset model info from data factory, including underlying data source, SQL query, and table schema.

```bash
bytedcli aeolus dataset-model-info [options]
```

**Options:**
- `-r, --region <region>` - Region: cn, sg, va, mycis, mybd, sglark, usttpusts (required)
- `--app-id <appId>` - Aeolus app ID (required, from list-authorized JSON output `app.id`)
- `--dataset-id <dataSetId>` - Dataset ID (required)
- `--json` is a global option and must appear before `aeolus`

**Examples:**
```bash
# Get dataset model info (VA region)
bytedcli aeolus dataset-model-info -r va --app-id 1000252 --dataset-id 2109028

# Get dataset model info with JSON output
bytedcli --json aeolus dataset-model-info -r cn --app-id 1005563 --dataset-id 4961129
```

**Output:**
- `baseConf`: Dataset basic configuration (name, owner, description, etc.)
- `nodeConf`: Data source configuration including:
  - `dataSourceType`: e.g., "hive", "click_house"
  - `dbName`: Database name
  - `tbName`: Table name
  - `query`: Underlying SQL query (if any)
  - `fields`: Field schema with types
  - `partitionConfList`: Partition configuration
- `modelType`: Model type (0 = standard)

**Use cases:**
- Trace metric calculation logic back to underlying data source
- Understand the SQL transformation between raw tables and dataset fields
- Debug data discrepancies by examining the underlying query

---

### query

Execute SQL query against a dataset.

```bash
bytedcli aeolus query <datasetId> <sql> [options]
```

**Arguments:**
- `datasetId` - Dataset ID
- `sql` - SQL query string

**Options:**
- `-r, --region <region>` - Region: cn, sg, va, mycis, mybd, sglark, usttpusts (required)
- `--json` is a global option and must appear before `aeolus`
- `--version <version>` - API version (default: "v2")
- `--limit <limit>` - Limit rows in output (default: 100)

**Important:** there are two query paths:
- **Logical dataset SQL**: may work for some datasets, especially simpler pre-materialized ones.
- **Physical-table SQL**: often the reliable path for report/dataQuery URLs and for datasets whose semantic fields do not map directly to queryable identifiers.

**Examples:**
```bash
# Logical dataset SQL may work for some datasets
bytedcli aeolus query -r va 1576311 "SELECT \`[p_date]\`, \`[scene]\` FROM \`[DatasetName]\` WHERE \`[p_date]\` = '2026-03-01' LIMIT 5"

# Physical-table SQL is the reliable fallback when logical SQL fails
bytedcli aeolus query -r va 1576311 "SELECT reporting_ad_id, max(pangle_rolling3d_dollar_cost) AS pangle_rolling3d_dollar_cost FROM \`aeolus_data_db_xxx\`.\`aeolus_data_table_xxx\` WHERE p_date = '2026-03-01' GROUP BY reporting_ad_id ORDER BY pangle_rolling3d_dollar_cost DESC LIMIT 10"
```

**Output:**
- Column headers
- Data rows in table format

---

## SQL Syntax

Aeolus uses ClickHouse SQL syntax, but the table/field syntax depends on whether you are querying a logical dataset alias or the backing physical table.

### Logical dataset names may not be queryable

Some datasets accept logical SQL like:
```sql
FROM `[Dataset Name]`
SELECT `[field_name]`
```

But many report/dataQuery-backed datasets do **not**. Common failure signatures include:
- `unknownTable`
- `unknownIdentifier` / missing field errors
- `SELECT * LIMIT 1` only returning `dummy`

When you see those signals, switch to physical-table discovery instead of continuing to debug the logical alias.

### Physical-table SQL

The reliable fallback is to query the physical table directly after locating it via `dataset-model-info` and `system.query_log`:
```sql
FROM `aeolus_data_db_xxx`.`aeolus_data_table_xxx`
SELECT reporting_ad_id, sum(placement_dollar_cost_1d/100000) AS cost
```

### Partition Fields

If a dataset or physical table has partition fields (for example `p_date`), include them in the `WHERE` clause whenever applicable:
```sql
WHERE p_date = '2026-03-01'
```

### Recommended workflow for report/dataQuery URLs

1. Use `resolve-report` to map the URL to dataset IDs.
2. Use `dataset-fields` to inspect semantic fields and partition fields.
3. Use `dataset-model-info` to inspect `nodeConf[].query`, lineage, and source-table hints.
4. If logical SQL fails or only returns `dummy`, query `system.query_log` to find the backing physical table.
5. Query the physical `aeolus_data_db_*`.`aeolus_data_table_*` table directly.

### End-to-end fallback example

```bash
# Resolve the report URL
bytedcli aeolus resolve-report -r va --url "https://aeolus-va..."

# Inspect the dataset fields
bytedcli aeolus dataset-fields -r va 2231500

# Inspect the model / source logic
bytedcli aeolus dataset-model-info -r va --app-id 555116 --dataset-id 2231500

# Locate the physical table from query_log
bytedcli aeolus query -r va 2231500 "SELECT event_time, query FROM system.query_log WHERE query LIKE '%aeolus_data_table_%' ORDER BY event_time DESC LIMIT 50"

# Query the physical table directly
bytedcli aeolus query -r va 2231500 "SELECT reporting_ad_id, sum(placement_dollar_cost_1d/100000) AS cost FROM \`aeolus_data_db_xxx\`.\`aeolus_data_table_xxx\` WHERE p_date = '2026-04-07' AND placement = 'Pangle' GROUP BY reporting_ad_id ORDER BY cost DESC LIMIT 5"
```

---

## Query Editor

Ad-hoc SQL under `aeolus query-editor`. Uses QE HTTP APIs under `{baseUrl}/qe/v2/api/...` where `baseUrl` comes from the same region map as dataset commands (`src/api/aeolus/site.ts`).

**Auth:** Reuses `bytedcli auth login` (Titan passport cookie) for most regions. **`mycis`**, **`mybd`** and **`usttpusts`** use **session** auth instead (local browser cookies); see `references/invocation.md` for `--site` / `BYTEDCLI_CLOUD_SITE`.

**QE App ID:** Request header `x-qe-appid` defaults from `QE_APP_ID` or `BYTEDCLI_AEOLUS_QE_APP_ID` (CLI default in code if unset). Match the **Query Editor page URL `appId=`** when reproducing browser runs.

### `aeolus query-editor query run`

```bash
bytedcli aeolus query-editor query run [options]
```

**Required (soft-required by CLI):**

- `--file-id <id>` — Query file (`block_id` in API body)
- `--folder-id <id>` — Folder (`page_id` in API body)

**Common options:**

- `-r, --region <region>` — `cn` | `sg` | `va` | `mycis` | `mybd` | `sglark` | `usttpusts` (default `cn` if omitted)
- `--sql <sql>` — Inline SQL
- `--file <path>` — SQL from disk (if neither `--sql` nor `--file`, CLI may read SQL from the file record)
- `--queue <name>` — **Hive (default):** YARN queue name in `yarn.queue`. **CH (`--engine ch`):** maps to `cluster_name` unless `--cluster-name` is set
- `--idc <idc>` — **Hive only:** IDC in `yarn.idc`
- `--engine <engine>` — `hive` (default) or `ch` (ClickHouse runner: `/ch/task/run` instead of `/hive/task/run`)
- `--cluster-name <name>` — **CH only:** overrides `cluster_name` in submit body (otherwise use `--queue`)
- `--ch-region <code>` — **CH only:** `region` field in submit body (e.g. `VA`); if omitted, derived from `-r`
- `--no-wait` — Submit only; do not poll
- `--rows <N>` — Poll/display row cap for status polling path
- `--timeout <seconds>` — Poll timeout

**Engines:**

| `--engine` | Submit URL suffix | Body highlights |
|------------|-------------------|-----------------|
| `hive` (default) | `/hive/task/run` | `yarn`: `queue`, `idc`, `cluster_id`, plus `query`, `query_template`, … |
| `ch` | `/ch/task/run` | `cluster_name`, `region`, `page_id`, `block_id`, `query`, `query_template`, `task_name`, `template_conf` |

For **`ch`**, `cluster_name` must be non-empty: provide **`--queue`** and/or **`--cluster-name`**.

### `aeolus query-editor query status`

```bash
bytedcli aeolus query-editor query status [options]
```

**Required:** `--task-id`, `--file-id`, `--folder-id`

**Options:** `-r/--region`, `--rows`, and the same **`--engine` / `--cluster-name` / `--ch-region`** as `query run`. **Must match the engine used for submit**, otherwise the wrong `/hive/task/.../status` vs `/ch/task/.../status` path is used.

### `aeolus query-editor query logs`

```bash
bytedcli aeolus query-editor query logs [options]
```

**Required:** `--task-id`

**Options:** `-r/--region`, **`--engine`** (and optional `--cluster-name`, `--ch-region` for consistency with other QE commands). **Must match the engine used for submit.**

### `aeolus query-editor query one`

Creates a temp folder + file, writes SQL, then runs `query run` with polling.

**Required:** `--sql`

**Options:** `-r/--region`, `--folder`, `--name`, `--queue`, `--idc`, `--timeout`, `--rows`, plus **`--engine`**, **`--cluster-name`**, **`--ch-region`** (forwarded to the internal `query run`).

### ClickHouse example (align with browser QE)

```bash
export QE_APP_ID=<appIdFromQueryEditorUrl>
# Often for VA/SG on TikTok row:
# export BYTEDCLI_CLOUD_SITE=i18n-tt

bytedcli aeolus query-editor query run -r va --engine ch \
  --queue <cluster_name> \
  --folder-id <folderId> --file-id <fileId> \
  --file ./query.sql

bytedcli aeolus query-editor query status -r va --engine ch \
  --task-id <taskId> --file-id <fileId> --folder-id <folderId>
```

Other `query-editor` subcommands (`whoami`, `queues`, `datasources`, `folder`, `file`) are unchanged by `--engine`; only **`query run` / `status` / `logs` / `one`** accept engine flags.

---

## Resource Types

| Type | Description |
|------|-------------|
| `dashboard` | Aeolus dashboard |
| `data_set` | Aeolus dataset |

## Regions

Default OpenAPI / QE **hostnames** (see `src/api/aeolus/site.ts`). Developer console URLs may differ; use the console link for your tenant when creating ClientID/Secret.

| Region | Description | Default API host |
|--------|-------------|------------------|
| `cn` | China | `https://data.bytedance.net` |
| `sg` | Singapore (TikTok row) | `https://aeolus-sg.tiktok-row.net` |
| `va` | US East (TikTok row) | `https://aeolus-va.tiktok-row.net` |
| `mycis` | MYCIS | `https://aeolus-mycis.byteintl.net` |
| `mybd` | MYBD | `https://aeolus-mybd.sinf.net` |
| `sglark` | Singapore Lark | `https://aeolus-sglark.bytedance.net` |
| `usttpusts` | US TTP USTS | `https://aeolus-tx.tiktok-usts.net` |

## Authentication

Aeolus uses ClientID/ClientSecret authentication.

### ClientID/ClientSecret

1. Visit the Aeolus Developer Console to get your credentials:
   - **CN**: https://data.bytedance.net/aeolus/pages/developer/console/certification
   - **SG**: https://aeolus-sg.tiktok-row.net/pages/developer/console/certification (tenant-specific; may also use `aeolus-sg.bytedance.net` for some accounts)
   - **VA**: https://aeolus-va.tiktok-row.net/pages/developer/console/certification
   - **MYCIS**: https://aeolus-mycis.byteintl.net/#/developer/console/certification
   - **SGLARK**: https://aeolus-sglark.bytedance.net/pages/developer/console/certification
   - **USTTPUSTS**: https://aeolus-tx.tiktok-usts.net/pages/developer/console/certification

2. Configure in `.aeolus.env` file (choose one location):
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
BYTEDCLI_AEOLUS_MYCIS_CLIENT_ID=your_mycis_client_id
BYTEDCLI_AEOLUS_MYCIS_CLIENT_SECRET=your_mycis_client_secret
BYTEDCLI_AEOLUS_MYBD_CLIENT_ID=your_mybd_client_id
BYTEDCLI_AEOLUS_MYBD_CLIENT_SECRET=your_mybd_client_secret
BYTEDCLI_AEOLUS_SGLARK_CLIENT_ID=your_sglark_client_id
BYTEDCLI_AEOLUS_SGLARK_CLIENT_SECRET=your_sglark_client_secret
BYTEDCLI_AEOLUS_USTTPUSTS_CLIENT_ID=your_usttpusts_client_id
BYTEDCLI_AEOLUS_USTTPUSTS_CLIENT_SECRET=your_usttpusts_client_secret
```

## JSON Output

Use `--json` flag for structured output:

```bash
bytedcli --json aeolus list-authorized -r va
```

Output structure:
```json
{
  "status": "success",
  "data": {
    "resources": [...],
    "total": 100,
    "region": "va"
  },
  "context": {
    "execution_time_ms": 500,
    "timestamp": "2026-03-10T10:00:00.000Z"
  }
}
```
