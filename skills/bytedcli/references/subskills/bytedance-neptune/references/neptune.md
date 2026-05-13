# Neptune

Neptune 用于服务治理配置查询（安全/稳定性/限流/调度），支持跨站点（CN/BOE/ByteIntl）排查差异。

## 环境与站点

Use global `--site` to select the ByteCloud deployment. Per-service `--neptune-site` is a hidden alias for backward compatibility.

- CN: `--site cn`（默认）
- BOE: `--site boe`
- ByteIntl: `--site byteintl`

站点差异（bytedcli 内部已处理）：

- CN/BOE：API host 在 ByteCloud 控制台域名下（`cloud.bytedance.net` / `cloud-boe.bytedance.net`），请求需要 `x-bcgw-tenant-id: bytedance`
- ByteIntl：API host 为 `cloud.byteintl.net`，请求不需要 `x-bcgw-tenant-id`

## 站点/VRegion 自动发现（best-effort）

命令：`neptune list-sites`

bytedcli 会调用平台 meta 接口 `list_platform_vregions?platform=neptune`（并缓存 1 天）来尽量列出支持的站点与 VRegion。

## zones/vregions 列表（best-effort）

命令：`bytedcli --site <site> neptune list-cp-regions`

用于查询 Neptune 当前站点支持的 `zones` 与 `vregions` 列表，便于为后续配置查询选择正确的 `--zone`。

## 命令映射

- `neptune security`：安全配置（支持 `--method`，默认 `*`；支持 `--direction ingress|egress`）
- `neptune stability`：稳定性配置（支持 `--direction ingress|egress`）
- `neptune rate-limit`：限流配置（支持 `--direction ingress|egress`；`--v2` 仅对 ingress 生效）
- `neptune dispatch`：调度配置（支持 `--direction ingress|egress`）

