# APM

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

# 上下游服务依赖分析（deps）
bytedcli apm service deps --psm "example.service.api"                          # 查看上下游全部依赖
bytedcli apm service deps --psm "example.service.api" --direction upstream     # 仅上游
bytedcli apm service deps --psm "example.service.api" --direction downstream   # 仅下游
bytedcli apm service deps --psm "example.service.api" --range 6h              # 自定义时间范围
bytedcli apm service deps --psm "example.service.api" --region "China-North"   # 过滤机房
bytedcli --json apm service deps --psm "example.service.api"                   # JSON 输出

# 接口维度 SLA 分析（methods）
bytedcli apm service methods --psm "example.service.api"                                # 查看所有方法 SLA
bytedcli apm service methods --psm "example.service.api" --min-success-rate 99.9        # 仅显示成功率 < 99.9% 的方法
bytedcli apm service methods --psm "example.service.api" --latency                       # 同时查看方法 P99 延迟（默认单位 ms）
bytedcli apm service methods --psm "example.service.api" --latency --top 10              # 只看 Top 10（按 Max QPS）
bytedcli apm service methods --psm "example.service.api" --latency --method QueryFoo     # 只看指定方法（可重复/逗号分隔）
bytedcli apm service methods --psm "example.service.api" --range 6h --region "China-North"  # 自定义范围和机房
bytedcli --json apm service methods --psm "example.service.api"                         # JSON 输出

# i18n-bd 站点查询（deps / methods / qps / preview 均支持）
bytedcli --site i18n-bd apm service deps --psm "example.service.api"
bytedcli --site i18n-bd apm service methods --psm "example.service.api"
bytedcli --site i18n-bd apm service qps --psm "example.service.api"
bytedcli --site i18n-bd apm service preview --psm "example.service.api"

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

## apm service deps

查看服务的上下游依赖关系，包含每个依赖的 QPS、错误率和成功率。

| 选项 | 说明 |
|---|---|
| `--psm <psm>` | **必填**，服务 PSM |
| `--direction <dir>` | `upstream`、`downstream` 或 `both`（默认 both） |
| `--start <time>` | 开始时间（epoch / RFC3339 / `-1h`） |
| `--end <time>` | 结束时间（epoch / RFC3339） |
| `--range <duration>` | 相对时间范围（如 `1h`、`6h`、`12h`、`1d`） |
| `--region <region...>` | 过滤机房（可多次指定） |

输出内容：
- **Downstream Services**: 下游服务列表，含 Service、QPS、Error Rate、Success Rate
- **Upstream Services**: 上游服务列表，同上

## apm service methods

查看服务每个 method 的 QPS 和成功率，支持按成功率阈值过滤异常接口。

| 选项 | 说明 |
|---|---|
| `--psm <psm>` | **必填**，服务 PSM |
| `--min-success-rate <percent>` | 仅显示成功率低于此阈值的方法（如 `99.9`） |
| `--top <n>` | 仅显示 Top N（按 Max QPS） |
| `--method <method>` | 只看指定方法（可多次指定/逗号分隔） |
| `--latency` | 输出方法 P99 延迟（默认指标 `service.request.server.latency.total`，单位 ms） |
| `--latency-metric [name]` | 自定义延迟指标（可选，默认 `service.request.server.latency.total`） |
| `--start <time>` | 开始时间 |
| `--end <time>` | 结束时间 |
| `--range <duration>` | 相对时间范围 |
| `--region <region...>` | 过滤机房（可多次指定） |

输出内容：
- **Service Methods**: 方法列表，含 Method、QPS、Success Rate
- 若无 per-method 数据，输出 Warning 提示
