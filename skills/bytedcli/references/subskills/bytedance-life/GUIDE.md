---
name: bytedance-life
description: "Operate 生活服务生财有数平台 via bytedcli, including the 直播数据工作台 live-screen tools. Use when tasks mention 生活服务, 生财有数, live-screen, 直播数据工作台, live room GMV, live key metrics, traffic/conversion/refund metrics, fetching summary metrics for a 直播间 ID, or resolving user info by 主播 ID / 抖音号 / 直播间 ID / 主播昵称."
---

# bytedcli Life

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

- 获取生活服务生财有数平台中直播数据工作台里的直播间核心指标
- 获取主播信息，支持主播 ID、主播抖音号、直播间 ID、主播昵称
- 用户给出直播间 ID，想看 GMV、订单、支付人数、GPM、CTR、CVR、ACU、PCU、互动、退款率等指标
- 用户给出主播昵称、主播 ID、抖音号或直播间 ID，想拿统一的用户字段
- 需要把浏览器 live-screen key metrics 接口转成 CLI / JSON 输出

## 前置条件

- 先完成可复用浏览器会话登录：`bytedcli auth login --session --auto`
- 普通 SSO token 登录不一定足够，因为 live-screen 接口复用 Data portal 浏览器 Cookie
- 临时复现浏览器请求时可设置 `BYTEDCLI_LIFE_COOKIE`
- 不要把完整 Cookie 放进命令行参数、skill 文档、MR 描述或日志

> 执行前缀见 `references/invocation.md`；下面示例直接写 `bytedcli`。

## Quick start

```bash
# 文本模式默认展示工作台默认指标
bytedcli life live-screen summary --room-id 1234567890

# 展示全部指标，并按指标组过滤
bytedcli life live-screen summary --room-id 1234567890 --all --group 交易指标

# 机器可读输出
bytedcli --json life live-screen summary --room-id 1234567890

# 按主播昵称搜索用户
bytedcli life live-screen user-info --nickname sample-anchor --count 10

# 按直播间 ID 或主播 ID 获取用户信息
bytedcli life live-screen user-info --room-id 1234567890
bytedcli life live-screen user-info --user-id sample-user-id
```

## Notes

- `life` 是生活服务生财有数平台的工具集，`live-screen` 是直播数据工作台的工具集，`summary` 用于获取核心指标，`user-info` 用于获取用户信息
- 用户可见命令名使用短横线：`live-screen`、`user-info`，MCP flat tool name 会自动映射为 `life_live_screen_summary`、`life_live_screen_user_info`
- `--json` 是全局参数，必须放在 `life` 前面
- 文本模式默认只展示 `meta.extra.default=true` 的指标，`--all` 会展示接口返回的全部指标
- `user-info` 只暴露 `user_info` 与昵称搜索结果的共同字段，其中包含 `live_list`；`--nickname` 可能返回多条结果，`--count` 只在昵称搜索时生效
- `self_compare` 是 ratio，文本模式展示时会乘以 `100` 并加 `%`
- `unit: "%"` 的 `value` 已经是百分数，不要再次乘以 `100`
- 指标外层 key、内层 `key`、`meta.dataIndex` 偶尔不一致，读取时优先按 `meta.dataIndex` 排序和展示，找不到时再按 `meta.dataKey` / 内层 `key` fallback

## References

- `references/invocation.md`
- `references/life.md`
- `references/troubleshooting.md`
