# APM Metric 探索与高级查询

`apm metric` 支持完整的探索式查询连招（Tenant -> Metric -> Tags -> TagValues），以及最终通过前端页面复制出的 Query DSL 进行时序数据查询。工具内置了动态路由能力，并支持防漂移时间窗及多机房查询。

## 5大命令连招 (探索工作流)

在使用 APM 查询指标时，往往面临"知道大概长什么样，但拼不出完整名字或 tag"的窘境。通过组合使用下面 5 个探索指令，你可以一步步拿到最终需要的查询语句。

1. **查租户 (tenant-list)**:
   列出当前控制面所有可用的指标租户。通常默认使用 `default`，特定场景如 runtime 可能会在 `apm.runtime` 等租户下。
   ```bash
   bytedcli apm metric tenant-list
   ```

2. **找对名字 (search)**:
   只知道部分指标名前缀时，用 `search` 搜索找出全名：
   ```bash
   bytedcli apm metric search --prefix "life.alliance.commission_base"
   bytedcli --site i18n-tt apm metric search --prefix "pipo.wallet.portal.requestV2"
   ```

3. **查多值字段与 Tag Keys (field-list / tagk-list)**:
   多值指标（multi-field metric）是指在同一个指标名和维度（Tags）下，同时记录了多个不同的值（Field，如 pct50, pct95, pct99）。使用 field-list 可查询支持的 field 列表；使用 tagk-list 可查询可用的分组维度 (Tag Keys)。
   
   **判断是否是多值指标有两种方法**：
   1. 先查 field-list，如果返回结果非空，说明是多值指标
   2. 先尝试 query，如果报错提示 multi-field，再查 field-list
   
   ```bash
   bytedcli --site i18n-tt apm metric field-list --metric "pipo.wallet.portal.requestV2.latency"
   bytedcli apm metric tagk-list --metric "life.alliance.commission_base.throughput_rate"
   # 查询非 default 租户的多值字段
   bytedcli apm metric field-list --tenant iaas.vnet_tob --metric "toutiao.iaas.vpc_broker.api_call"
   ```

4. **查特定 Tag 的合法值 (tagv-list)**:
   知道有某个维度，但不确定具体枚举值时，用 `tagv-list` 查值：
   ```bash
   bytedcli apm metric tagv-list --metric "life.alliance.commission_base.throughput_rate" --tags [实际tag名称]
   ```

5. **组装最终查询 (query)**:
   拿到指标名、聚合方式、Group By 和 Filter 后，组合成 query 命令获取时序数据：
   ```bash
   # CN 控制面单值指标查询
   bytedcli apm metric query "sum:life.alliance.commission_base.throughput_rate{[实际tag名称]=literal_or(*),}{}" --duration 1h
   
   # i18n-tt 控制面多值指标查询（Throughput）
   bytedcli --site i18n-tt apm metric query "sum:pipo.wallet.portal.requestV2.throughput{country_code=literal_or(*),}{_psm=literal_or(pipo.wallet.portal)}" --duration 6h --region Singapore-Compliance --region Singapore-Central
   
   # i18n-tt 控制面多值指标查询（Latency 加权 P99）
   bytedcli --site i18n-tt apm metric query "weighted_avg(value=pct99,weight=counter):pipo.wallet.portal.requestV2.latency{country_code=literal_or(*),}{_psm=literal_or(pipo.wallet.portal)}" --duration 6h --region Singapore-Compliance --region Singapore-Central
   
   # 查询非 default 租户的指标（需指定 --tenant）
   bytedcli apm metric query "avg:toutiao.iaas.vpc_broker.api_call{action=literal_or(*)}{}[num.delta_counter.rate]" --tenant iaas.vnet_tob --duration 30m
   ```

## 租户（Tenant）选项

`apm metric` 的探索命令（`search`、`field-list`、`tagk-list`、`tagv-list`）和查询命令（`query`）均支持 `--tenant` 选项，用于指定指标所属的租户命名空间。

- **默认值**：`default`（向后兼容，不传时等同于 `--tenant default`）
- **使用场景**：当指标注册在非 default 租户下（如 `iaas.vnet_tob`、`apm.runtime`），必须显式指定 `--tenant` 才能查到数据
- **适用命令**：`search`、`field-list`、`tagk-list`、`tagv-list`、`query`

```bash
# 探索非 default 租户的指标元数据
bytedcli apm metric field-list --tenant iaas.vnet_tob --metric "toutiao.iaas.vpc_broker.api_call"
bytedcli apm metric tagk-list --tenant iaas.vnet_tob --metric "toutiao.iaas.vpc_broker.api_call"
bytedcli apm metric tagv-list --tenant iaas.vnet_tob --metric "toutiao.iaas.vpc_broker.api_call" --tags action

# 查询非 default 租户的时序数据
bytedcli apm metric query "avg:toutiao.iaas.vpc_broker.api_call{action=literal_or(*)}{}[num.delta_counter.rate]" \
  --tenant iaas.vnet_tob --duration 1h
```

## 参数格式（防幻觉警告）

注意：**`apm metric query` 绝对没有 `--psm` 和 `--query` 这两个 flag。**
查询语句必须是 **位置参数 (Positional Argument)** 直接紧跟在 `apm metric query` 之后。过滤条件（如 PSM、Method 等）必须写在 query 的标签（大括号 `{}`）内。

错误示范（幻觉）：
`bytedcli apm metric query --psm "xxx" --query "service.request.server.throughput.total"`

**正确示范：**
`bytedcli apm metric query "service.request.server.throughput.total{_psm=literal_or(xxx)}" --duration 30m`

## 动态路由与多机房查询

`apm metric` 系列命令原生支持动态路由能力，你只需切换 `--site` (如 `cn`, `i18n-tt`, `boe`)，底层会自动路由到对应的租户与指标网关。

多机房查询时，支持多次声明 `--region` 参数以组装数组：
- **国内环境** (默认 `--site cn`): `--region China-North --region China-East`
- **海外环境** (`--site i18n-tt` 等): `--region MY-Compliance --region Singapore-Central`

## 多种黄金组合 Demo

### Demo 1: 基本防漂移查询
针对单个 PSM 进行查询，带有 `[delta]` 多值语法并使用 `--duration` 来控制防漂移时间窗（注意：多值后缀 `[delta]` 必须放在末尾）：
```bash
bytedcli apm metric query "bytedtrace.sdk.span.server.rate{_psm=literal_or(example.demo.api)}{}[delta]" --duration 1h
```

### Demo 2: 多 Region 联合查询并开启 group-by-region
跨多个 Region 查询，并按机房分组显示数据：
```bash
bytedcli apm metric query "bytedtrace.sdk.span.server.rate{_psm=literal_or(example.demo.api)}{}" \
  --region China-North --region China-East \
  --group-by-region \
  --duration 30m
```

### Demo 3: 指定绝对时间区间的精确历史查询
使用 `--start-time` 和 `--end-time`（传入秒级时间戳）精确圈定时间范围：
```bash
bytedcli apm metric query "bytedtrace.sdk.span.server.latency.us.pct99{_psm=literal_or(example.demo.api)}{}" \
  --start-time 1700000000 \
  --end-time 1700003600 \
  --region China-North
```

### Demo 4: 非 default 租户的多值指标查询
查询注册在 `iaas.vnet_tob` 租户下的 VPC Broker API 调用速率，按 action 分组：
```bash
bytedcli apm metric query "avg:toutiao.iaas.vpc_broker.api_call{action=literal_or(*)}{}[num.delta_counter.rate]" \
  --tenant iaas.vnet_tob \
  --duration 30m
```

## 常见指标查询范式

- **统计类型的多值指标**：用 `[delta] + sum` 求总量，用 `[rate] + sum` 求 QPS。
- **rate 类型的单值指标**：直接用 `sum` 求 QPS。
- **counter 类型的单值指标**：
  - 使用 `rate{counter}` 或 `rate(counter)` 前缀来算 QPS，示例：`sum:rate{counter}:top-10-max:pipo.wallet.portal.request{method=literal_or(*)}{}`
  - 使用 `rate{counter,diff}` 前缀来算 Sum，示例：`sum:rate{counter,diff}:top-10-max:pipo.wallet.portal.request{method=literal_or(*)}{}`

## 常见指标 (Common Metrics)

Agent 在执行任务时，可以优先使用以下内部常用的指标。

### Server 端指标
- **QPS**: `bytedtrace.sdk.span.server.rate`
- **Latency (us)**: `bytedtrace.sdk.span.server.latency.us` (常用后缀 `.pct99` 获取 99 分位)
- **入流量 (Bytes)**: `bytedtrace.sdk.span.server.receive.bytes`
- **出流量 (Bytes)**: `bytedtrace.sdk.span.server.send.bytes`
- **常用 Tag**: `_psm` (所在服务名), `_method` (接口名), `_from_service` (上游调用方 PSM), `_status_code` (状态码), `_is_error` (0:成功, 1:失败)

### Client 端指标
- **QPS**: `bytedtrace.sdk.span.client.rate`
- **Latency (us)**: `bytedtrace.sdk.span.client.latency.us`
- **入流量 (Bytes)**: `bytedtrace.sdk.span.client.receive.bytes`
- **出流量 (Bytes)**: `bytedtrace.sdk.span.client.send.bytes`
- **常用 Tag**: `_psm` (所在服务名), `_to_service` (下游被调服务名), `_to_method` (下游接口名)

### Panic 与 Runtime 指标
- **Panic 次数**: `runtime.go.panics` (注：需在特定租户 apm.runtime 下使用)
  - 常用 Tag: `role` (server/client), `from_service`, `to_service`, `method`

## Query 语法提取规则

对于 `metric` 的 Query 表达式（如前端页面复制的内容），提取规则与语法如下：

### 过滤操作符 (Filter Operators)
在编写过滤条件时，**必须使用** `key=func(value)` 的格式，**禁止**使用 `key=value` 这种简单格式。默认推荐使用 `literal_or`。

常见的过滤操作符及区别如下：
- `literal_or`：精确匹配多个值，大小写敏感。例如 `_psm=literal_or(example.api,example.rpc)`。
- `iliteral_or`：精确匹配多个值，大小写不敏感。例如 `country_code=iliteral_or(us,my)`。
- `regexp`：支持正则过滤。例如 `_psm=regexp(example\..*)`。

**特殊用法：**
- 按某个 tag 分组但不过滤：使用 `key=literal_or(*)`
- 例如：`country_code=literal_or(*)` 表示按 country_code 分组，显示所有国家

### 双花括号 `{}` 语法规则
在使用指标查询时，`{}` 的顺序有严格含义：
- 第一个 `{}`：**分组 (Group By) 并过滤**。放在这里的 Tag Key，最终返回的数据会按它拆线/分组。格式为 `key=func(value)`。
- 第二个 `{}`：**仅过滤 (Filter Only)**。放在这里的 Tag Key 只用于缩小数据范围，但不会按它分组。
- 同一个 Tag Key 可以在两个 `{}` 里同时出现。

### 方括号 `[xxx]` 语法规则 (单值 vs 多值)
- **多值指标 (Multi-field)**：如果涉及时间聚合或特定 field（例如 `[delta]`、`[rate]`），**必须将其放在整个表达式的末尾**。例如 `metric_name{group_by}{filter_only}[delta]`。
- **单值指标 (Single-field)**：常规单值指标**完全没有结尾的方括号**。例如 `metric_name{group_by}{filter_only}`。

确保在调用参数中，严格遵守上述规则使用完整的 Query 字符串，以触发内置的 DSL 解析器。
