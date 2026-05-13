---
name: bytedance-libra
description: "Operate Libra/DataTester A/B testing platform via bytedcli: create experiments, view experiment details, report data with metrics/P-Value/significance, search experiments, manage test users, approve or reject experiment peer reviews. Use when tasks mention Libra, A/B test, experiment, flight, metric group, DataTester, create experiment, experiment report, P-Value, significance, traffic allocation, test user, peer review, approve experiment, reject experiment, or when users ask about experiment results, want to check if an experiment is statistically significant, need to find experiments, analyze metric trends, or approve/reject a peer review."
---

# bytedcli Libra

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

Libra (DataTester) A/B 实验平台 CLI，通过 SSO 认证访问，无需额外凭证。

## When to use

- 查看实验详情、流量分配、版本配置
- 查看实验报告：指标数据、P-Value、显著性判断
- 分析指标趋势：逐日累计或分段趋势
- 搜索 / 筛选实验
- 管理实验测试用户

## Prerequisites

- 通用调用方式见 `references/invocation.md`
- 首次使用：`bytedcli auth login`（device login；后续自动复用）

> 下面示例直接写 `bytedcli`，实际执行前缀见 `references/invocation.md`。

## Workflows

### 判断实验是否显著

这是最常见的场景：用户想知道某个实验的指标是否有统计显著的提升。

```bash
# 0. 创建实验（通过 JSON 文件传入完整请求体）
bytedcli --json libra experiment create --app-id -1 --request-file ./experiment.json
# 创建成功后，从返回的 JSON 中提取实验 ID，拼接实验链接给用户：
# https://data.bytedance.net/libra/flight/<experiment_id>/report/main

# 1. 查看实验基本信息
bytedcli libra experiment get --flight-id <flight_id>

# 2. 列出可用指标组（找到目标指标组 ID）
bytedcli libra experiment report --flight-id <flight_id>

# 3. 查看指标组报告（含 P-Value 和显著性标记）
bytedcli libra experiment report --flight-id <flight_id> --metric-group <metric_group_id>

# 4. 如需看趋势变化
bytedcli libra experiment report --flight-id <flight_id> --metric-group <metric_group_id> --trend
```

报告中 `Sig` 列按学术惯例分级：`*` p<0.05 / `**` p<0.01 / `***` p<0.001。

### 跨机房实验报告（data_region）

Libra 后端按机房路由查询；`lean-data-v2` 接口必须传正确的 `data_region`，否则会"静默"返回全空数据（所有 metric 的 `value=null`，且 `end_date` 被 clamp 到旧日期）。CLI 会自动从实验的 `truly_effected_regions` 推导 `data_region`，大多数时候无需手动指定；只有当自动推导结果与实际不符时才用 `--data-region` 覆盖。

```bash
# 自动推导（EU_TTP flight 会自动用 eu_ttp，无需额外参数）
bytedcli --site i18n-tt libra experiment report --flight-id <flight_id> --metric-group <metric_group_id>

# 手动指定（强制某个 region）
bytedcli --site i18n-tt libra experiment report --flight-id <flight_id> --metric-group <metric_group_id> --data-region eu_ttp
```

支持的 `data_region` 取值与实验 `truly_effected_regions` 的映射：

| `truly_effected_regions` | `data_region` | 说明 |
|---|---|---|
| `SG` | `sg` | Singapore (TTP-SG) |
| `VA` | `va` | Virginia / US（老 US 机房） |
| `US_TTP` | `us_ttp` | US-TTP（对应 `tx` 别名也接受） |
| `EU_TTP` | `eu_ttp` | EU-TTP（GCP 欧洲机房） |
| `MY` | `my` | My-Compliance |
| 多区域 / 无明确区域 | `other` | 默认值 |

**典型排查**：如果 report 全 `-`，先 `bytedcli libra experiment get --flight-id <id>` 看 `truly_effected_regions`，再确认 `--data-region` 的取值匹配。手动传 `--data-region other` 可以快速复现老行为（作为对照）。

### 查看指标组信息

```bash
# 先从实验报告里拿到 metric group ID
bytedcli libra experiment report --flight-id <flight_id>

# 再查看指标组基础信息
bytedcli libra metric-group get --id <metric_group_id>
```

### 查看指标组模版

```bash
# 查看指标组模版（默认 normal 类型）
bytedcli libra metric-group template get --id <template_id> --app-id <app_id>

# 查看 conclusion 类型的指标组模版
bytedcli libra metric-group template get --id <template_id> --app-id <app_id> --type conclusion

# 直接传模版页面 URL
bytedcli libra metric-group template get --url <template_url>
```

### 查看实时指标

查看实验的实时监控数据（默认最近 1 小时）。

```bash
# 1. 列出实验可用的实时仪表盘
bytedcli libra experiment realtime --flight-id <flight_id>

# 2. 查看仪表盘详情（获取指标组 ID）
bytedcli libra experiment realtime --dashboard-info <dashboard_id>

# 3. 查看特定指标组的实时数据
bytedcli libra experiment realtime --flight-id <flight_id> --metric-group <metric_group_id>

# 指定时间范围
bytedcli libra experiment realtime --flight-id <flight_id> --metric-group <metric_group_id> \
  --start "2026-04-08 10:00:00" --end "2026-04-08 11:00:00"

# 分钟级数据
bytedcli libra experiment realtime --flight-id <flight_id> --metric-group <metric_group_id> --period-type m

# 查看指标含义（显示指标描述）
bytedcli libra experiment realtime --flight-id <flight_id> --metric-group <metric_group_id> --describe

# 列出所有可用的实时仪表盘
bytedcli libra experiment realtime --list-dashboards

# 查看仪表盘详情及 SQL 定义（帮助理解指标计算逻辑）
bytedcli libra experiment realtime --dashboard-info <dashboard_id> --show-sql
```

### 搜索并查看实验

```bash
# 列出可用 App
bytedcli libra app list

# 按名称搜索实验
bytedcli libra experiment list --app-id <app_id> --search "example-experiment"

# 按参数 key 搜索（跨所有 App）
bytedcli libra experiment list --app-id -1 --search "example-config-key" --search-type config

# 按创建者 / 状态筛选（1=运行中, 2=已停止, 3=已暂停, 4=草稿）
bytedcli libra experiment list --app-id <app_id> --creator "demo.user" --status 1
```

### 管理测试用户

```bash
# 查看测试用户
bytedcli libra test-user list --flight-id <flight_id>

# 添加测试用户
bytedcli libra test-user add --flight-id <flight_id> --uid <uid>

# 删除测试用户
bytedcli libra test-user delete --flight-id <flight_id> --uid <uid>

# 指定版本（多实验组时需要）
bytedcli libra test-user add --flight-id <flight_id> --uid <uid> --version <vid>
```

### 按参数路径搜索实验

```bash
# 模糊搜索：包含该路径的实验
bytedcli libra experiment search --key-path "example.feature_toggle"

# 精确匹配
bytedcli libra experiment search --key-path "example.feature_toggle" --exact-match

# 只看运行中的（默认 1=运行中 + 3=已暂停）
bytedcli libra experiment search --key-path "example.feature_toggle" --status 1
```

### 批准 / 驳回实验 peer review

```bash
# 推荐：直接传 peer-review 页面 URL，自动解析 flight/review/app ID
bytedcli libra experiment approve --url https://libra-<region>.tiktok-row.net/libra/peer-review/<flight_id>/view/<review_id>

# 驳回（默认是批准）
bytedcli libra experiment approve --url <peer_review_url> --reject

# 手动传 review 和 app ID（无 URL 时）
bytedcli libra experiment approve --review-id <review_id> --app-id <app_id>
```

## Command overview

| Command | Description |
|---------|-------------|
| `libra experiment create --app-id <id> --request-file <path>` | 创建实验（JSON 直传） |
| `libra experiment get --flight-id <id>` | 实验详情（版本、流量、owner） |
| `libra experiment traffic --flight-id <id>` | 流量分配和版本权重 |
| `libra experiment report --flight-id <id>` | 实验报告（指标、P-Value、趋势） |
| `libra experiment realtime --flight-id <id>` | 实时指标（最近 1 小时监控数据） |
| `libra metric-group get --id <id>` | 指标组基础信息（文本摘要；`--json` 返回完整 payload） |
| `libra metric-group template get --id <id> --app-id <id>` | 指标组模版信息（支持 `--type normal\|conclusion`，默认 normal，403 自动 fallback） |
| `libra experiment list --app-id <id>` | 搜索和筛选实验 |
| `libra experiment search --key-path <path>` | 按参数路径搜索实验 |
| `libra experiment approve --url <url>` | 批准或驳回实验 peer review |
| `libra app list` | 列出所有可用 App |
| `libra test-user list --flight-id <id>` | 查看测试用户 |
| `libra test-user add --flight-id <id> --uid <uid>` | 添加测试用户 |
| `libra test-user delete --flight-id <id> --uid <uid>` | 删除测试用户 |

各命令的完整参数、选项和 `request-file` 格式说明见 `references/libra.md`。

## Key notes

- `--json` 是全局选项，放在子命令前：`bytedcli --json libra experiment get --flight-id <flight_id>`
- 用户提到 `ROW`、`i18n`、`US` 或 `TTP` 场景时，默认加 `--site i18n-tt`（例如：`bytedcli --site i18n-tt libra app list`）
- 任何需要 `--app-id` 的 Libra 命令，默认使用 `--app-id -1`，除非用户明确指定其他 app_id。
- report 默认 `--merge-type total`（累计，含 P-Value），可选 `sum`（日均）或 `avg`
- report `--trend` 显示逐日趋势，`total` 为累计趋势，`avg` 为分段趋势
- report `--data-region` 控制机房路由，默认从实验 `truly_effected_regions` 自动推导（EU_TTP→`eu_ttp` / SG→`sg` / VA→`va` / US_TTP→`us_ttp` / MY→`my` / 其它→`other`）；传错值会静默返回全空数据，排查空报告时首先检查这个
- 需要分维度报表时，先执行 `libra experiment report --flight-id <id> --metric-group <metric_group_id> --list-dimensions`，再用 `--dimension <dimension_id>` 或 `--dimension <dimension_id:value_id[,value_id...]>` 拉取维度数据
- 需要多维交叉时，重复传 `--dimension`；若只是分别查看两个维度，请各跑一条命令
- 多维交叉查询走异步 adhoc 计算，若超时就提示稍后重试同一条命令
- `metric-group get` 当前仅支持 `prod` 和 `i18n-tt`
- 访问 `i18n-tt` 时，请显式使用 `--site i18n-tt`

## Troubleshooting

常见错误和处理方式见 `references/troubleshooting.md`。典型问题：

- **metric-group get 需要完整结构化结果**：加 `--json`，文本模式默认只展示摘要
- **报告数据为空**：先确认 `truly_effected_regions` 与自动推导的 `--data-region` 匹配；若匹配但仍空，再考虑实验数据 T+1/T+2 延迟，或用 `libra experiment report --flight-id <id>` 检查可用指标组

## References

- `references/libra.md` — 各命令完整参数和选项
- `references/troubleshooting.md` — 常见错误和处理
- `references/invocation.md` — 通用调用方式和站点切换
