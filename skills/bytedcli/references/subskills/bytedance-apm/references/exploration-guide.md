# APM Metric 探索式查询与排障指南

在使用 APM 查询指标时，往往会面临“知道大概长什么样，但拼不出完整名字或 tag”的窘境。
本指南将向你展示一套“循循善诱”的探索工作流，通过组合使用不同指令，一步步拿到最终需要的查询语句。

## 典型工作流

如果你只知道部分指标名 -> 用 `search` 搜索全名 -> 用 `query` 查询 -> 报错提示 multi-field，用 `field-list` 查可用多值 -> 不知道能按什么过滤/分组，或者提示 tagKey 不存在，用 `tagk-list` 查所有可用的 tag -> 用 `tagv-list` 查某个 tag 的可用值 -> 最终再次组合 `query`。

### 如何判断是否是多值指标

判断一个指标是否是多值指标有两种方法：

1. **方法一：先查 field-list**
   执行 `field-list` 命令，如果返回结果非空，说明是多值指标，需要在查询时加上方括号 `[field]`

2. **方法二：通过 query 报错判断**
   先尝试不带方括号执行 `query`，如果报错提示 "multi-field" 相关信息，再回去查 `field-list`

下面用两个真实业务场景来演示：

### 场景一：CN 控制面单值指标查询

假设我们要查询 `life.alliance.commission_base.throughput_rate` 这个指标：

#### 第一步：找对名字 (search)

只知道指标前缀是 `life.alliance.commission_base`，先用前缀搜索找出完整指标名：

```bash
bytedcli apm metric search --prefix "life.alliance.commission_base"
```
从结果中找到了需要的指标：`life.alliance.commission_base.throughput_rate`。

#### 第二步：检查是否是多值指标 (field-list)

先通过 field-list 判断是否是多值指标：

```bash
bytedcli apm metric field-list --metric "life.alliance.commission_base.throughput_rate"
```
如果返回结果为空，说明这是一个单值指标，不需要方括号 `[field]`。

#### 第三步：查可用的 Tag Keys (tagk-list)

查看这个指标支持哪些 tag：

```bash
bytedcli apm metric tagk-list --metric "life.alliance.commission_base.throughput_rate"
```
你可以在结果中找到该指标实际支持的维度名称（可能没有 `country_code`）。

#### 第四步：查特定 Tag 的合法值 (tagv-list)

查看某个 tag 的可用值：

```bash
bytedcli apm metric tagv-list --metric "life.alliance.commission_base.throughput_rate" --tags [实际tag名称]
```

#### 第五步：组装最终查询 (query)

现在组装查询命令，按实际的维度分组，查询过去 1 小时的数据：

```bash
bytedcli apm metric query "sum:life.alliance.commission_base.throughput_rate{[实际tag名称]=literal_or(*),}{}" --duration 1h
```

**重要说明：**
- 第一个 `{}`：**分组并过滤**，这里放 `[实际tag名称]=literal_or(*)` 表示按这个 tag 分组
- 第二个 `{}`：**仅过滤**，这里可以放额外的过滤条件
- 不要使用 `key=value` 这种格式，统一使用 `key=func(value)` 的形式，推荐用 `literal_or`

---

### 场景二：i18n-tt 控制面多值指标查询

假设我们要查询 `pipo.wallet.portal.requestV2.throughput`（throughput 指标）和 `pipo.wallet.portal.requestV2.latency`（latency 指标），或者 `pipo.cashloan.prod.common_handler.throughput` 这类 handler 指标：

#### 第一步：找对名字 (search)

在 i18n-tt 控制面按前缀搜索：

```bash
bytedcli --site i18n-tt apm metric search --prefix "pipo.wallet.portal.requestV2"
# 或者搜索 cashloan 相关指标
bytedcli --site i18n-tt apm metric search --prefix "pipo.cashloan.prod"
```
从结果中找到了需要的指标。

#### 第二步：检查是否是多值指标 (field-list)

先通过 field-list 判断是否是多值指标：

```bash
bytedcli --site i18n-tt apm metric field-list --metric "pipo.cashloan.prod.common_handler.throughput"
```
如果返回结果非空，说明是多值指标，需要在查询时加上方括号 `[field]`。

#### 第三步：查可用的 Tag Keys (tagk-list)

查看指标支持哪些 tag：

```bash
bytedcli --site i18n-tt apm metric tagk-list --metric "pipo.cashloan.prod.common_handler.throughput"
```
你可以在结果中找到类似 `country_code`, `method`, `_psm` 等维度名称。

**注意**：这类指标通常需要指定 `_psm` tag 才能查询。

#### 第四步：查特定 Tag 的合法值 (tagv-list)

查看 `method` tag 的可用值：

```bash
bytedcli --site i18n-tt apm metric tagv-list --metric "pipo.cashloan.prod.common_handler.throughput" --tags method
```
你会看到类似 `GetMainPage` 等方法名（注意是 GetMainPage 而不是 MainPage）。

#### 第五步：组装最终查询 (query)

**查询 Throughput（QPS），按 country_code 分组，过滤 GetMainPage：**

```bash
bytedcli --site i18n-tt apm metric query "sum:pipo.cashloan.prod.common_handler.throughput{country_code=literal_or(*),method=literal_or(GetMainPage)}{_psm=literal_or(pipo.cashloan.prod)}[delta]" --duration 1h --region Singapore-Central
```

**重要说明：**
- 第一个 `{}`：**分组并过滤**，这里放 `country_code=literal_or(*)` 表示按 country_code 分组，同时 `method=literal_or(GetMainPage)` 过滤特定方法
- 第二个 `{}`：**仅过滤**，这里放 `_psm=literal_or(pipo.cashloan.prod)` 只用于缩小范围
- 不要使用 `key=value` 这种格式，统一使用 `key=func(value)` 的形式，推荐用 `literal_or`
- 如果是单值指标，不需要方括号 `[field]`

### 过滤操作符说明与 `{}` 语法进阶

在编写过滤条件时，**必须使用** `key=func(value)` 的格式，**不要**使用 `key=value` 这种简单格式。默认推荐使用 `literal_or`。

以下是常见过滤操作符：
- `literal_or`：精确匹配多个值，大小写敏感。例如 `_psm=literal_or(pipo.wallet.portal,pipo.cashloan.prod)`。
- `iliteral_or`：精确匹配多个值，大小写不敏感。例如 `country_code=iliteral_or(us,my)`。
- `regexp`：支持正则过滤。

**特殊用法：**
- 按某个 tag 分组但不过滤：使用 `key=literal_or(*)`
- 例如：`country_code=literal_or(*)` 表示按 country_code 分组，显示所有国家

#### 双花括号 `{A}{B}` 语法解析

在使用指标查询时，`{}` 的顺序有严格含义：
- 第一个 `{}`：**分组 (Group By) 并过滤**。放在这里的 Tag Key，最终返回的数据会按它拆线/分组。
- 第二个 `{}`：**仅过滤 (Filter Only)**。放在这里的 Tag Key 只用于缩小数据范围，但不会按它分组。
- 同一个 Tag Key 可以在两个 `{}` 里同时出现。

举个例子：如果你想按 `country_code` 拆线（分组），同时只需要看 `_psm` 为 `pipo.wallet.portal` 且 `method` 为 `GetMainPage` 的数据：
第一步，把 `country_code=literal_or(*)` 和 `method=literal_or(GetMainPage)` 放入第一个 `{}`（分组并过滤）`。
第二步，把 `_psm=literal_or(pipo.wallet.portal)` 放入第二个 `{}`（仅过滤）。

通过这套流程，你可以自主探索所有 APM 指标细节。

## 场景补充：海外站点与多 Region 查询

### 先区分 `--site` 和 `--region`

- `--site` 决定走哪个控制面和哪套 SSO。
- `--region` 决定实际查询哪个机房 / vregion。
- 海外常用组合：
  - `--site i18n-tt --region Singapore-Central|Singapore-Compliance|MY-Compliance`
  - `--site eu-ttp --region EU-TTP2`
  - `--site us-ttp --region US-TTP`

补充说明：
- `euttp2` 会自动归一化为 `EU-TTP2`
- `ttp1` 会自动归一化为 `US-TTP`
- 文档和脚本里仍建议优先使用 canonical region：`EU-TTP2`、`US-TTP`

### 海外站点基础探索

如果只是先确认站点下有哪些 metric，可先做租户和前缀搜索：

```bash
# i18n-tt
bytedcli --site i18n-tt apm metric tenant-list
bytedcli --site i18n-tt apm metric search --prefix "pipo.cashloan.prod.state"

# eu-ttp
bytedcli --site eu-ttp apm metric tenant-list
bytedcli --site eu-ttp apm metric search --prefix "bytedtrace.sdk.span.client.latency"

# us-ttp
bytedcli --site us-ttp apm metric tenant-list
bytedcli --site us-ttp apm metric search --prefix "bytedtrace.sdk.span.client.latency"
```

### EU 站点查询 `euttp2`

下面示例使用 `eu-ttp` 控制面查询 `euttp2` 机房。CLI 会自动把 `euttp2` 归一化成 `EU-TTP2`：

```bash
# 先看这个 metric 支持哪些 tag
bytedcli --site eu-ttp apm metric tagk-list \
  --metric "bytedtrace.sdk.span.client.latency.us.pct99"

# 查询 ad.lift.engine 调下游服务的 client P99 延时
bytedcli --site eu-ttp apm metric query \
  "avg:bytedtrace.sdk.span.client.latency.us.pct99{_to_service=literal_or(*)}{_psm=literal_or(ad.lift.engine)}" \
  --duration 1h \
  --region euttp2
```

### US 站点查询 `ttp1`

下面示例使用 `us-ttp` 控制面查询 `ttp1` 机房。CLI 会自动把 `ttp1` 归一化成 `US-TTP`：

```bash
# 先看这个 metric 支持哪些 tag
bytedcli --site us-ttp apm metric tagk-list \
  --metric "bytedtrace.sdk.span.client.latency.us.pct99"

# 查询 ad.lift.engine 调下游服务的 client P99 延时
bytedcli --site us-ttp apm metric query \
  "avg:bytedtrace.sdk.span.client.latency.us.pct99{_to_service=literal_or(*)}{_psm=literal_or(ad.lift.engine)}" \
  --duration 1h \
  --region ttp1
```

### 多 Region 联合查询

当需要跨多个机房联查时，通过多次声明 `--region` 参数来指定要查询的 region。推荐在 `i18n-tt` 控制面下做海外联查：

```bash
# 查询 Singapore-Compliance 和 Singapore-Central 两个 region 的数据，按 country_code 分组
bytedcli --site i18n-tt apm metric query \
  "sum:pipo.cashloan.prod.state_monitor.loan_order{country_code=literal_or(*)}{}" \
  --duration 6h \
  --region Singapore-Compliance \
  --region Singapore-Central
```

如果要联查 SG / EU / US 三个海外机房，可以直接多次传 `--region`：

```bash
# 联查 ad.lift.engine 在 SG / EU / US 三侧的下游 client P99
bytedcli --site i18n-tt apm metric query \
  "avg:bytedtrace.sdk.span.client.latency.us.pct99{_to_service=literal_or(*)}{_psm=literal_or(ad.lift.engine)}" \
  --duration 1h \
  --region Singapore-Central \
  --region EU-TTP2 \
  --region US-TTP
```

海外常用的 region 包括：
- `Singapore-Compliance`
- `Singapore-Central`
- `MY-Compliance`
- `EU-TTP2`
- `US-TTP`
- `US-East-Compliance`
