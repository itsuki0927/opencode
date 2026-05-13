---
name: bytedance-fundeye
description: "Operate FundEye / Fullink workflows via bytedcli: get rule detail, get diff detail, list diffs by rule and time range, and list alarms. Use this skill whenever the user mentions FundEye, Fullink, TCheck, rule reconciliation, diff detail, diff list, alarm list, rule_id, diff_id, or wants to inspect reconciliation rules and discrepancy records from FundEye."
---

# bytedcli FundEye

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

- 查询 FundEye / Fullink 核对规则详情
- 查询某条 diff 的明细
- 按规则、时间范围分页查询 diff 列表
- 查询告警列表
- 用户提到 `rule_id`、`diff_id`、`alarm_order_id`、核对规则、差异详情、差异列表、FundEye、Fullink

## 能力范围

当前 skill 覆盖以下命令：

- 规则详情：`fundeye rule get`
- 差异详情：`fundeye diff get`
- 差异列表：`fundeye diff list`
- 告警列表：`fundeye alarm list`

## 前置条件

- 使用通用调用方式：`references/invocation.md`
- 首次使用前先确保 `bytedcli auth login` 已完成
- FundEye 请求依赖当前登录态自动补 `x-jwt-token` 和 `UserName`
- `fundeye diff list` 目前要求显式传时间范围：`--start` 和 `--end`

> 执行前缀见 `references/invocation.md`；下面示例直接写 `bytedcli`。

## 工作流约定

1. 需要机器可读输出时默认加 `--json`，并把它放在 `fundeye` 前面。
2. 规则详情优先用 `fundeye rule get --rule-id <id>`。
3. diff 明细优先用 `fundeye diff get --diff-id <id> --rule-id <id>`。
4. diff 列表必须提供 `--rule-id --start --end`，必要时再补 `--rule-version`、`--alarm-order-id`。
5. 如果服务端返回 500，优先保留 `request_id` 给后端排查，不要先假设是 CLI 组参错误。

## Quick start

```bash
# 规则详情
bytedcli --json fundeye rule get --rule-id 2604202570843580

# diff 明细
bytedcli --json fundeye diff get \
  --diff-id "DOUBLE_DS_CHECK#^#0#^#demo-diff" \
  --rule-id 2601142357560097

# diff 列表
bytedcli --json fundeye diff list \
  --rule-id 2601142357560097 \
  --rule-version 11 \
  --start "2026-04-21 00:00:00" \
  --end "2026-04-22 00:00:00" \
  --page 1 \
  --page-size 20

# 告警列表
bytedcli --json fundeye alarm list --page 1 --page-size 20
```

## 常见工作流

### 1. 查看规则

- 使用 `fundeye rule get --rule-id <id>`
- 优先关注 `baseInfo` 和 `graphData`
- `layoutInfo`、内部原始 `raw` 不再对外输出

### 2. 查看某条 diff

- 已知 `diff_id` 且知道所属规则时，用 `fundeye diff get`
- 如果只有告警单和规则信息，先用 `fundeye diff list` 缩小范围，再取具体 `diffId`

### 3. 按规则排查 diff

- 使用 `fundeye diff list --rule-id <id> --start <time> --end <time>`
- 需要进一步缩小范围时，加 `--rule-version` 或 `--alarm-order-id`
- 对结果中的 `diffId` 再调用 `fundeye diff get`

### 4. 先看告警，再查 diff

- 先执行 `fundeye alarm list`
- 取返回里的 `alarmOrderId`、`ruleId`
- 再执行 `fundeye diff list --rule-id ... --alarm-order-id ... --start ... --end ...`

## Notes

- `--json` 是全局参数，必须放在 `fundeye` 前面，例如 `bytedcli --json fundeye rule get --rule-id ...`
- `fundeye diff` 现在是分组命令；详情请用 `fundeye diff get`，列表请用 `fundeye diff list`
- `fundeye diff list` 缺少必填参数时会返回结构化 help JSON
- 如果 diff/list 返回 `HTTP 500`，通常说明服务端业务侧异常，优先记录 `request_id`

## References

- `references/fundeye.md`
- `references/invocation.md`
- `references/troubleshooting.md`
