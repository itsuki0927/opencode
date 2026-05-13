# FundEye 命令说明

## 当前覆盖能力

- `fundeye rule get --rule-id <rule-id>`
- `fundeye diff get --diff-id <diff-id> --rule-id <rule-id>`
- `fundeye diff list --rule-id <rule-id> --start <time> --end <time>`
- `fundeye alarm list`

## 参数约定

### 规则详情

```bash
bytedcli --json fundeye rule get --rule-id 2604202570843580
```

- 对外参数统一使用 `--rule-id`
- JSON 输出不再包含 `layoutInfo`、`raw`

### diff 明细

```bash
bytedcli --json fundeye diff get \
  --diff-id "DOUBLE_DS_CHECK#^#0#^#demo-diff" \
  --rule-id 2601142357560097
```

- `fundeye diff` 是分组命令，详情查询必须走 `diff get`
- JSON 输出不再包含 `raw`

### diff 列表

```bash
bytedcli --json fundeye diff list \
  --rule-id 2601142357560097 \
  --rule-version 11 \
  --alarm-order-id "2601142357560097##20260421065000##1_2##11" \
  --start "2026-04-21 00:00:00" \
  --end "2026-04-22 00:00:00" \
  --page 1 \
  --page-size 20
```

- `--rule-id`、`--start`、`--end` 必填
- `--rule-version`、`--alarm-order-id` 可选
- JSON 输出当前保留：
  - `diffs`
  - `current`
  - `page_size`
  - `total`
  - `actual_diff_cnt`
  - `diff_money`
  - `alarm_condition`
- JSON 输出不再包含：
  - `diff_money_tips`
  - 每个 diff item 的 `raw`

### 告警列表

```bash
bytedcli --json fundeye alarm list --page 1 --page-size 20
```

- 支持分页
- 支持按产品和优先级过滤

## 使用建议

- 需要机器可读结果时，优先加 `--json`
- 先看告警，再查 diff 时，推荐流程是：
  - `fundeye alarm list`
  - `fundeye diff list`
  - `fundeye diff get`
