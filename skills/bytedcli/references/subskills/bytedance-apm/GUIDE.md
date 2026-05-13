---
name: bytedance-apm
description: "Operate APM via bytedcli: service preview, QPS, upstream/downstream dependency analysis, per-method SLA (success rate, QPS), Redis monitoring dashboards, runtime/TLB/TCC/MySQL/AGW monitoring via Byteheart and Argos, and APM metric querying (with Query DSL, anti-drift duration, multi-region). Use when tasks mention APM, service monitoring, QPS, dependencies, SLA, success rate, metric query, or Redis monitoring."
---

# bytedcli APM

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

- 服务预览、QPS 查询
- 上下游服务依赖分析（deps：查看服务的 upstream/downstream 依赖及其 QPS、错误率、成功率）
- 接口维度 SLA 分析（methods：查看每个 method 的 QPS、成功率，支持按成功率阈值过滤）
- Metric 指标高级查询（Query DSL）及 Metric 探索 (search, field-list, tagk-list, tagv-list)
- Redis 监控（overview/client/server/proxy）
- 运行时 / 中间件监控（runtime/TLB/TCC/MySQL/AGW）

## 前置条件

- 使用通用调用方式：`references/invocation.md`

> 执行前缀见 `references/invocation.md`；下面示例直接写 `bytedcli`。

## Quick start

Commands are grouped under `apm service`, `apm redis`, and `apm metric`. Old flat names (e.g. `apm service-preview`, `apm redis-qps`) still work as hidden aliases.

```bash
# 服务预览
bytedcli apm service preview --psm "psm.name" --service-type redis

# QPS
bytedcli apm redis qps --psm "cache.demo.redis"
bytedcli apm redis traffic --psm "cache.demo.redis"
bytedcli apm service qps --psm "example.service.api"
bytedcli apm service qps --psm "example.service.api" --metric "service.request.server.throughput.total"
bytedcli apm service downstream-qps --psm "example.service.api"
bytedcli apm service downstream-qps --psm "example.service.api" --metric "service.request.downstream.throughput.total"

# 上下游服务依赖分析
bytedcli apm service deps --psm "example.service.api"
bytedcli apm service deps --psm "example.service.api" --direction upstream
bytedcli apm service deps --psm "example.service.api" --direction downstream
bytedcli apm service deps --psm "example.service.api" --range 6h
bytedcli apm service deps --psm "example.service.api" --region "China-North"

# 接口维度 SLA 分析
bytedcli apm service methods --psm "example.service.api"
bytedcli apm service methods --psm "example.service.api" --min-success-rate 99.9
bytedcli apm service methods --psm "example.service.api" --latency
bytedcli apm service methods --psm "example.service.api" --latency --top 10
bytedcli apm service methods --psm "example.service.api" --latency --method "QueryHotelDetail"
bytedcli apm service methods --psm "example.service.api" --range 6h --region "China-North"

# i18n-bd 站点查询（deps / methods / qps / preview 均支持）
bytedcli --site i18n-bd apm service deps --psm "example.service.api"
bytedcli --site i18n-bd apm service methods --psm "example.service.api"

# Metric 基础查询（带必要的 _psm tag）
bytedcli apm metric query "bytedtrace.sdk.span.server.rate{_psm=literal_or(pipo.wallet.portal)}{}" --duration 1h --region "China-North"

# Redis 监控
bytedcli apm redis overview --psm "cache.demo.redis"
bytedcli apm redis client --psm "cache.demo.redis"
bytedcli apm redis server --psm "cache.demo.redis"
bytedcli apm redis proxy --psm "cache.demo.redis"

# 运行时 / 中间件
bytedcli apm service preview --psm "psm.name" --service-type runtime
bytedcli apm service preview --psm "psm.name" --service-type tlb
bytedcli apm service preview --psm "psm.name" --service-type tcc
bytedcli apm service preview --psm "psm.name" --service-type mysql
bytedcli apm service preview --psm "psm.name" --service-type agw_sidecar
```

## Metric 探索工作流

如果你不确定具体的 metric 名称或 tag，请按以下步骤探索：
1. 查租户 → `tenant-list`
2. 找 metric → `search`
3. 查 tag keys → `tagk-list`
4. 查 tag values → `tagv-list`
5. 查询数据 → `query`

完整的探索指南和高级用法请参考：[exploration-guide.md](./references/exploration-guide.md)、[metric.md](./references/metric.md)

## Notes

- `apm service deps` 基于 Argos measurement 接口，输出上下游依赖（按 service 聚合）。
  - QPS：`service.request.{downstream|upstream}.throughput.total`
  - Error QPS：`service.request.{downstream|upstream}.throughput.error`
  - Success Rate：基于 `service.request.{downstream|upstream}.error_rate`（成功率 = `100 - error_rate`），避免用数量做除法带来的偏差。
- `apm service methods` 基于 Argos measurement 接口，输出 method 维度指标（按 `method` / `service.method` 聚合，必要时自动 fallback）。
  - Success Rate：基于 `service.request.server.error_rate`（成功率 = `100 - error_rate`，两位小数）。
  - 延迟：用 `--latency` 打开（默认指标 `service.request.server.latency.total`，并自动转成 `ms`）。
  - `--top <n>`：按 `Max QPS` 排序取前 N。
  - `--method <name>`：只看指定方法（可重复/逗号分隔）。
- `apm service deps` 和 `apm service methods` 均支持 `--site i18n-bd`（映射到 mycis region）和 `--site i18n-tt` 海外查询，以及 `--region`、`--range`、`--start`/`--end` 时间窗参数。
- `apm metric query` 的查询语句是**位置参数**，且**不支持** `--psm` 与 `--query` 参数，请直接将过滤条件（如 `_psm=...`）写在 query 的标签内。
- 部分指标（如 `bytedtrace.sdk.span.server.rate`）有 tag rewrite 逻辑，**必须指定 `_psm` tag** 才能查询，例如：`bytedtrace.sdk.span.server.rate{_psm=literal_or(pipo.wallet.portal)}{}`
- **Metric 查询格式说明**：
  - 格式：`aggregator:metric_name{分组并过滤}{仅过滤}[multi_field]`
  - 第一个 `{}`：**分组并过滤**，格式为 `key=func(value)`，分组用 `key=literal_or(*)`
  - 第二个 `{}`：**仅过滤**，只用于缩小范围，不分组
  - **必须使用** `key=func(value)` 格式，**禁止**使用 `key=value` 简单格式
  - 常用 func：`literal_or`（精确匹配）、`iliteral_or`（忽略大小写）、`regexp`（正则）
- `apm metric query` 支持直接输入前端页面中的 Query DSL 进行解析（支持 `[xxx]` 等多值语法提取），支持 `--duration` 参数提供防漂移时间窗，并且支持 `--region` 多次声明以组装数组进行多机房查询。
- `apm service preview/runtime/tlb/tcc/mysql/agw-sidecar` 调用 Byteheart 全局视图接口
- Redis 相关命令返回 Grafana/Argos 监控入口链接（按集群维度）
- `apm service qps` 基于 Argos measurement 接口，可用 `--metric` 指定指标，支持使用 `--region` 参数过滤 vregion；现已支持通过 `--site i18n-tt` 进行海外控制面查询。支持传入多个机房进行正则聚合查询（通过多次指定 `--region A --region B`，或直接传入 `China-North|Singapore-Central` 格式）
- `apm service downstream-qps` 基于 Argos measurement 接口，默认指标为 `service.request.downstream.throughput.total`，用于查看服务调用下游依赖的 QPS，同样支持 `--region` 参数过滤 vregion 以及 `--site i18n-tt` 海外查询。支持传入多个机房进行正则聚合查询（通过多次指定 `--region A --region B`，或直接传入 `China-North|Singapore-Central` 格式）
- `apm redis qps/traffic` 基于 Cache 服务详情的当前统计值
- 需要结构化输出加 `--json`（全局选项，放在子命令之前，如 `bytedcli --json apm service qps ...`）

## References

- [apm.md](./references/apm.md)
- [metric.md](./references/metric.md)
- [exploration-guide.md](./references/exploration-guide.md)
- [invocation.md](./references/invocation.md)
- [troubleshooting.md](./references/troubleshooting.md)
