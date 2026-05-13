---
name: bytedance-neptune
description: "Operate Neptune via bytedcli: list sites/zones, fetch security/stability/rate-limit/dispatch configs for ingress/egress, list lane groups (所有泳道组), and list lanes (某个泳道组下的泳道) across CN/BOE/ByteIntl. Use when tasks mention Neptune governance, stability, dispatch, rate limit, security, lane groups, or lanes."
---

# bytedcli Neptune

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

- Neptune 平台：安全/稳定性/限流/调度配置排查
- 同时关注入流量（ingress）与出流量（egress）
- 跨环境（CN/BOE/ByteIntl）排查配置差异
- 查询泳道组（lane groups）列表
- 查询某个泳道组下的泳道（lanes）

## 前置条件

- 使用通用调用方式：`references/invocation.md`
- 需要鉴权的命令先登录：`bytedcli auth login`

## Quick start

```bash
# 发现 Neptune 支持的站点（best-effort）
bytedcli neptune list-sites

# 查看某个站点支持的 zones/vregions（best-effort）
bytedcli --site cn neptune list-cp-regions
bytedcli --site boe neptune list-cp-regions
bytedcli --site byteintl neptune list-cp-regions

# 安全配置（method 默认 *；direction 默认 ingress）
bytedcli neptune security --psm example.service.api --cluster default --zone CN --method "*" --direction ingress

# 稳定性配置
bytedcli neptune stability --psm example.service.api --cluster default --zone CN --direction ingress

# 限流配置（v2 仅对 ingress 生效）
bytedcli neptune rate-limit --psm example.service.api --cluster default --zone CN --direction ingress
bytedcli neptune rate-limit --psm example.service.api --cluster default --zone CN --direction ingress --v2

# 调度配置
bytedcli neptune dispatch --psm example.service.api --cluster default --zone CN --direction ingress

# 泳道组列表（问：当前有哪些泳道组？）
bytedcli neptune lane-group list
bytedcli neptune lane-group list --page 2 --page-size 20

# 泳道列表（问：某个泳道组下有哪些泳道？）
bytedcli neptune lane list --domain-code domain-adies --zone CN
bytedcli neptune lane list --domain-code domain-adies --zone CN --page 2 --page-size 50

# 切换环境（BOE/ByteIntl）
bytedcli --site boe neptune stability --psm stone.openapi.toolbox_backend --cluster faas-cn-north --zone BOE --direction egress
bytedcli --site byteintl neptune stability --psm your.psm --cluster default --zone TEXAS --direction ingress

# 需要结构化输出时加 --json
bytedcli --json neptune stability --psm example.service.api --cluster default --zone CN
bytedcli --json neptune lane-group list
bytedcli --json neptune lane list --domain-code domain-adies --zone CN
```

## Notes

- 使用全局 `--site` 选择站点（`cn|boe|byteintl`，默认 `cn`）。Per-service `--neptune-site` is a hidden alias for backward compatibility.
- `--direction` 支持：`ingress|egress`（默认 `ingress`）
- `--zone` 建议显式传入；如不传，默认：`CN(cn/byteintl)`、`BOE(boe)`；可用 `neptune list-cp-regions` 查看可选值
- `--page` 和 `--page-size` 用于分页（`--page-count` 和 `--page-num` 是隐藏的兼容别名）
- `neptune lane list` 命令：
  - `--domain-code`: 域名代码（必填）
  - `--group-code`: 组代码（可选，默认同 domain-code）
  - `--zone`: 区域（必填）
  - `--lane-name`: 泳道名称过滤（可选）
  - `--logic-unit-name`: 逻辑单元名称（可选，默认 "default"）
  - `--psm`: PSM 过滤（可选）

## References

- `references/neptune.md`

