# Libra CLI Reference

## libra experiment create

通过 JSON 请求体创建新实验。

```bash
# 从 JSON 文件创建（--app-id 传 -1，实际 app_id 放在 body 内）
bytedcli --json libra experiment create --app-id -1 --request-file ./experiment.json

# 内联 JSON 创建
bytedcli --json libra experiment create --app-id -1 --request-json '{"name":"demo-exp", ...}'
```

**选项：**

| Option | Description |
|--------|-------------|
| `--app-id <id>` | Libra app ID，通常传 `-1`（实际 app_id 放在请求体内） |
| `--request-json <json>` | 内联 JSON 请求体 |
| `--request-file <path>` | 从文件读取 JSON 请求体 |

请求体会被自动包裹为 `{ "experiments": [body] }` 发送。

**request-file JSON 模板：**

```json
{
  "name": "实验名称",
  "manage_type": "strategy",
  "owners": [{"id": 12345, "name": "demo.user"}],
  "description": "实验描述",
  "expectation": "",
  "scene": 0,
  "feature_type": 3,
  "app_id": 495,
  "is_long_time_flight": 0,
  "enable_gradual": false,
  "specified_psms": [],
  "filter_rule": [
    {
      "conditions": [
        {
          "logic": "&&",
          "condition": {
            "key": "app_id",
            "op": "==",
            "value": [8478],
            "type": "int",
            "custom_filter": false,
            "source": "libra",
            "property_type": "common_param"
          }
        },
        {
          "logic": "&&",
          "condition": {
            "key": "version_code",
            "op": ">=",
            "value": 100190000,
            "type": "int",
            "custom_filter": false,
            "source": "libra",
            "property_type": "common_param"
          }
        }
      ],
      "logic": "||"
    }
  ],
  "filter_user_list": 2,
  "transmit": true,
  "version_traffic_adjustable": false,
  "metric_scene": 2,
  "strategy_category_ids": [],
  "small_traffic_link": "",
  "large_traffic_link": "",
  "is_mab": 0,
  "duration": 2592000,
  "version_resource": 0.01,
  "book_version_resource": 0,
  "experiment_mode": 1,
  "product_id": 1538,
  "layer_info": {
    "create_layer_auto": false,
    "product_id": 1538,
    "hash_strategy": "did",
    "layer_id": 194016
  },
  "versions": [
    {"name": "control", "description": "对照组", "type": 0, "config_show_mode": 1, "weight": 500, "config": "{}"},
    {"name": "treatment", "description": "实验组", "type": 1, "config_show_mode": 1, "weight": 500, "config": "{\"key\":{\"param\":true}}"}
  ],
  "metrics": [],
  "tags": [],
  "skip_verification": true
}
```

**关键字段说明：**

| 字段 | 说明 |
|------|------|
| `name` | 实验名称，全局唯一，最长 200 字符 |
| `manage_type` | `"strategy"`（服务端）或 `"product"`（客户端） |
| `owners` | 负责人数组，每项含 `id`（employee_id）和 `name` |
| `app_id` | Libra 应用 ID（即 Libra 平台的 libraKey，可在 [应用管理页](https://data.bytedance.net/libra/access?page=1&status=4) 查询，与客户端上报的 app_id 不同） |
| `product_id` | 产品线 ID（与 layer_info.product_id 一致） |
| `duration` | 实验时长，秒。30 天 = 2592000 |
| `version_resource` | 实验流量比例，0~1（0.01 = 1%） |
| `layer_info.layer_id` | 流量层 ID |
| `layer_info.hash_strategy` | 分流方式：`"did"` / `"uid"` |
| `versions[].type` | 0 = 对照组，1 = 实验组 |
| `versions[].weight` | 流量权重（千分比），按比例分配 |
| `versions[].config` | 参数配置 JSON 字符串 |
| `filter_rule` | 受众过滤规则数组，每个元素是一组 AND 条件 |
| `filter_rule[].conditions[].condition.op` | 操作符：`"=="`、`">="` 、`"in_bundle"` 等 |
| `metrics` | 关注指标组数组，可为空（重要指标会自动关联） |
| `skip_verification` | `true` 跳过前端校验 |

可通过 `bytedcli --json libra experiment get --flight-id <id>` 导出已有实验的完整字段结构作为参考模板。

## libra experiment get

查看实验详情，包含名称、状态、版本配置、owner、流量比例、标签等。

```bash
bytedcli libra experiment get --flight-id <flight_id>
bytedcli --json libra experiment get --flight-id <flight_id>
```

## libra experiment traffic

查看实验流量分配和版本权重。

```bash
bytedcli libra experiment traffic --flight-id <flight_id>
```

## libra experiment report

查看实验报告。不带 `--metric-group` 时列出所有可用指标组。

```bash
# 列出指标组
bytedcli libra experiment report --flight-id <flight_id>

# 查看具体指标组
bytedcli libra experiment report --flight-id <flight_id> --metric-group <metric_group_id>

# 指定日期和合并方式
bytedcli libra experiment report --flight-id <flight_id> --metric-group <metric_group_id> \
  --start 2026-03-18 --end 2026-03-25 --merge-type total

# 列出当前指标组支持的维度和值
bytedcli libra experiment report --flight-id <flight_id> --metric-group <metric_group_id> --list-dimensions

# 按维度拉取报告（查询该维度下全部值）
bytedcli libra experiment report --flight-id <flight_id> --metric-group <metric_group_id> --dimension <dimension_id>

# 只看指定维度值
bytedcli libra experiment report --flight-id <flight_id> --metric-group <metric_group_id> \
  --dimension <dimension_id:value_id1,value_id2>

# 多维交叉查询
bytedcli libra experiment report --flight-id <flight_id> --metric-group <metric_group_id> \
  --dimension <dimension_id:value_id1,value_id2> \
  --dimension <dimension_id:value_id3,value_id4>

# 查看逐日趋势
bytedcli libra experiment report --flight-id <flight_id> --metric-group <metric_group_id> --trend

# 指定机房（通常自动推导，不用传；只在自动推导错、或对比其它 region 时使用）
bytedcli libra experiment report --flight-id <flight_id> --metric-group <metric_group_id> --data-region eu_ttp
```

**选项：**

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `--flight-id <id>` | 实验 Flight ID（必填） | - |
| `--metric-group <id>` | 指标组 ID | 省略则列出所有 |
| `--start <YYYY-MM-DD>` | 开始日期 | 最新有数日期 |
| `--end <YYYY-MM-DD>` | 结束日期 | 最新有数日期 |
| `--merge-type <type>` | `total`(累计)/`sum`(日均)/`avg` | `total` |
| `--trend` | 显示逐日趋势数据 | 关闭 |
| `--list-dimensions` | 列出当前 metric group 可用维度和值 ID | 关闭 |
| `--dimension <spec>` | 维度选择器，格式 `<dimension_id>` 或 `<dimension_id:value_id[,value_id...]>`；重复传多个维度时执行交叉查询 | - |
| `--data-region <region>` | 机房路由：`sg` / `eu_ttp` / `us_ttp` / `tx` / `va` / `my` / `other` | 从实验 `truly_effected_regions` 自动推导，推不出时回退 `other` |
| `--wait-timeout-sec <sec>` | 多维交叉查询最长等待秒数 | `180` |
| `--poll-interval-sec <sec>` | 多维交叉查询轮询间隔秒数 | `5` |

说明：`--dimension <dimension_id>` 查询该维度下全部值；`--dimension <dimension_id:value_ids>` 只查询指定值；重复传多个 `--dimension` 时执行多维交叉。多维交叉查询走异步 adhoc 计算；若超时，命令会返回当前 `async_job_id` / `progress` / `status`，提示稍后重试同一条命令。

**`--data-region` 详解**：Libra 后端按机房路由查询，传错区域会静默返回 `value=null`（接口仍返回 `code: 0`），并把 `end_date` clamp 到旧日期。推导规则：

| 实验 `truly_effected_regions` | 自动选用的 `data_region` |
|---|---|
| `SG` / `sg` | `sg` |
| `VA` / `va` | `va` |
| `US_TTP` / `us_ttp` | `us_ttp` |
| `EU_TTP` / `eu_ttp` | `eu_ttp` |
| `MY` / `my` | `my` |
| 其他 / 无法推导 | `other`（默认兜底） |

只有自动推导错、或者手工对比不同 region 表现时才需要加 `--data-region`。

## libra metric-group get

查看指标组基础信息。文本模式输出 owner / metric / virtual table 摘要；`--json` 返回完整 payload。

```bash
# 按指标组 ID 查询
bytedcli libra metric-group get --id <metric_group_id>

# i18n-tt / TikTok ROW
bytedcli --site i18n-tt libra metric-group get --id <metric_group_id>
```

**选项：**

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `--id <id>` | Libra 指标组 ID（必填） | - |

说明：`metric-group get` 当前仅支持 `prod` 和 `i18n-tt`。文本模式默认展示摘要；需要完整结构化结果时加 `--json`。

## libra metric-group template get

查看指标组模版（metric-group template / bundle）详情。支持直接传 `--id` 或模板页面 / API `--url`。

```bash
# 按 template id 查询
bytedcli libra metric-group template get --id <template_id>

# 已知 app 时显式传入
bytedcli libra metric-group template get --id <template_id> --app-id <app_id>

# 查看 conclusion 类型的指标组模版
bytedcli libra metric-group template get --id <template_id> --app-id <app_id> --type conclusion

# 直接传模版页面 URL
bytedcli libra metric-group template get --url <template_url>

# 直接传 API URL
bytedcli libra metric-group template get --url <metric_group_bundle_api_url>

# i18n-tt / TikTok ROW
bytedcli --site i18n-tt libra metric-group template get --url <template_url>
```

**选项：**

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `--id <id>` | Metric group template ID；与 `--url` 二选一 | - |
| `--url <url>` | 模版页面 URL 或 `metric_group_bundle`/`conclusion_report_bundle` API URL；与 `--id` 二选一 | - |
| `--app-id <id>` | Libra App ID；已知时建议显式传入 | 自动解析 / probing |
| `--type <type>` | 模版类型：`normal`（metric_group_bundle）或 `conclusion`（conclusion_report_bundle） | `normal`，403 时自动 fallback 到 conclusion |

说明：省略 `--app-id` 时，会先尝试从模版页面解析 `app_id`，再查询 `metric_group_bundle` 模块下当前用户可访问的 app，最后才回退到 `-1`。两种模版类型使用不同的后端接口：`normal` 对应 `metric_group_bundle`，`conclusion` 对应 `conclusion_report_bundle`（返回层级分类结构和 conclusion 指标组）。不指定 `--type` 时默认 normal，403 时自动 fallback 到 conclusion。文本模式默认展示摘要；需要完整结构化结果时加 `--json`。
**报告字段说明：**

| 列 | 含义 |
|----|------|
| Metric | 指标名称 |
| Version | 实验组名称（对照组不显示，作为 baseline） |
| Mean | 指标均值 |
| Diff% | 相对对照组的变化百分比 |
| P-Value | 统计显著性 p 值 |
| CI | 置信区间 |
| Sig | `*` p<0.05 / `**` p<0.01 / `***` p<0.001 |

## libra experiment list

搜索和筛选实验。`--app-id` 为必填参数。

```bash
# 按 App 列出实验
bytedcli libra experiment list --app-id <app_id>

# 按名称搜索
bytedcli libra experiment list --app-id <app_id> --search "example-experiment"

# 按创建者筛选
bytedcli libra experiment list --app-id <app_id> --creator "demo.user"

# 按参数 key 搜索
bytedcli libra experiment list --app-id -1 --search "example-config-key" --search-type config

# 按状态筛选
bytedcli libra experiment list --app-id <app_id> --status 1
```

**选项：**

| 选项 | 说明 |
|------|------|
| `--app-id <id>` | Libra App ID（必填） |
| `-s, --search <keyword>` | 按名称搜索（数字自动识别为 ID 搜索） |
| `--search-type <type>` | 搜索类型：`id`/`name`/`vid`/`config` |
| `--status <n>` | 1=运行中, 2=已停止, 3=已暂停, 4=草稿 |
| `--creator <email>` | 按创建者邮箱前缀筛选 |
| `--page <n>` | 页码，默认 1 |
| `--page-size <n>` | 每页条数，默认 20 |

## libra experiment approve

批准或驳回实验的 peer review。支持传 peer-review 页面 URL 自动解析 `flight_id` / `review_id` / `app_id`，也可手动指定。

```bash
# 推荐：直接传 peer-review URL（从 URL 中提取 flight_id 和 review_id）
bytedcli libra experiment approve --url https://libra-<region>.tiktok-row.net/libra/peer-review/<flight_id>/view/<review_id>

# 驳回 review（默认是批准）
bytedcli libra experiment approve --url <peer_review_url> --reject

# 手动指定 review 和 app ID（无 URL 时使用）
bytedcli libra experiment approve --review-id <review_id> --app-id <app_id>
```

**选项：**

| 选项 | 说明 |
|------|------|
| `--url <url>` | Libra peer-review 页面 URL，自动解析 `flight_id` 和 `review_id` |
| `--review-id <id>` | Review ID；`--url` 未提供时必填 |
| `--flight-id <id>` | 实验 Flight ID；用于推导 `--app-id`，省略时走接口 probing |
| `--app-id <id>` | Libra App ID；省略时从 `--flight-id` 推导 |
| `--reject` | 驳回 review（默认是批准） |

说明：`--url`、`--review-id` 至少提供一个；传 `--url` 时会从 URL 解析出 `flight_id` 和 `review_id`，覆盖手动传入的同名参数。`<region>` 为 peer-review 站点区域（例如 `sg` / `va` / `us` / `eu`），通常与实验所在 site 一致。

## libra experiment search

按参数路径搜索包含指定配置参数的实验。

```bash
# 模糊搜索
bytedcli libra experiment search --key-path "example.feature_toggle"

# 精确匹配
bytedcli libra experiment search --key-path "example.feature_toggle" --exact-match

# 只看运行中的实验
bytedcli libra experiment search --key-path "example.feature_toggle" --status 1
```

**选项：**

| 选项 | 说明 |
|------|------|
| `--key-path <path>` | 参数路径（必填），如 `example.feature_toggle` |
| `--app-id <id>` | Libra App ID，默认 -1（所有 App） |
| `--exact-match` | 精确匹配路径，默认模糊匹配 |
| `--status <list>` | 逗号分隔的状态筛选：1=运行中, 2=已停止, 3=已暂停（默认 1,3） |
| `--page <n>` | 页码，默认 1 |
| `--page-size <n>` | 每页条数，默认 20 |

## libra app list

列出所有可用的 Libra App。

```bash
bytedcli libra app list
```

## libra test-user list

查看实验所有版本的测试用户。

```bash
bytedcli libra test-user list --flight-id <flight_id>
```

## libra test-user add

添加测试用户到实验版本。

```bash
bytedcli libra test-user add --flight-id <flight_id> --uid <uid>

# 指定版本（多实验组时需要）
bytedcli libra test-user add --flight-id <flight_id> --uid <uid> --version <vid>

# 多个 UID（逗号分隔或重复 --uid）
bytedcli libra test-user add --flight-id <flight_id> --uid uid1,uid2
```

## libra test-user delete

从实验版本中删除测试用户。

```bash
bytedcli libra test-user delete --flight-id <flight_id> --uid <uid>
bytedcli libra test-user delete --flight-id <flight_id> --uid uid1,uid2 --version <vid>
```

**test-user 选项：**

| 选项 | 说明 |
|------|------|
| `--flight-id <id>` | 实验 Flight ID（必填） |
| `--uid <uid>` | 测试用户 UID，可逗号分隔或重复使用（必填） |
| `--version <vid>` | 目标版本 ID 或名称（单实验组时自动选择） |
