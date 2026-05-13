# Life Commands

## live-screen user-info

```bash
bytedcli life live-screen user-info --nickname sample-anchor --count 10
bytedcli life live-screen user-info --user-id sample-user-id
bytedcli life live-screen user-info --display-id sample-display-id
bytedcli life live-screen user-info --room-id 1234567890
bytedcli --json life live-screen user-info --nickname sample-anchor --count 10
```

用途：在生活服务生财有数平台的直播数据工作台中获取用户信息。

参数：

- `--user-id <user-id>`：主播 ID
- `--display-id <display-id>`：主播抖音号
- `--room-id <room-id>`：直播间 ID
- `--nickname <nickname>`：主播昵称
- `--count <n>`：昵称搜索结果数量上限；只和 `--nickname` 一起使用
- `--live-limit <n>`：每个用户展示的直播记录数量上限；JSON 模式默认全部，文本模式默认 1 条
- `--pid <pid>`：覆盖 live-screen 页面 pid，一般不需要传
- `--portal-key <key>`：覆盖 Data portal key，一般不需要传

认证：

- 推荐先运行 `bytedcli auth login --session --auto`
- 命令会复用保存的浏览器会话，并尝试补齐 Data portal 所需 Cookie
- 本地调试可设置 `BYTEDCLI_LIFE_COOKIE`

输出：

- JSON 模式返回 `users`
- `users` 中每个元素只保留共同字段：`user_id`、`short_id`、`unique_id`、`nickname`、`avatar_uri`、`follower_count`、`follower_count_str`、`custom_verify`、`is_follow`、`live_list`
- `live_list` 中保留共同的直播记录字段：`room_id`、`create_time`、`start_time`、`finish_time`、`is_live`、`duration`、`is_life`、`gmv`、`title`
- JSON 模式默认返回完整 `live_list`；文本模式默认预览 `live_list` 的第一条直播记录
- `--nickname` 可能返回多条候选；其余 selector 默认返回单条结果

## live-screen summary

```bash
bytedcli life live-screen summary --room-id 1234567890
bytedcli life live-screen summary --room-id 1234567890 --all
bytedcli life live-screen summary --room-id 1234567890 --all --group 流量指标
bytedcli --json life live-screen summary --room-id 1234567890
```

用途：在生活服务生财有数平台的直播数据工作台中获取核心指标。

参数：

- `--room-id <room-id>`：直播间 ID，必填
- `--pid <pid>`：覆盖 live-screen 页面 pid，一般不需要传
- `--portal-key <key>`：覆盖 Data portal key，一般不需要传
- `--all`：文本模式展示全部指标；不传时只展示工作台默认指标
- `--group <group>`：文本模式按指标组过滤，例如 `交易指标`、`流量指标`
- `--limit <n>`：限制文本模式展示行数

认证：

- 推荐先运行 `bytedcli auth login --session --auto`
- 命令会复用保存的浏览器会话，并尝试补齐 Data portal 所需 Cookie
- 本地调试可设置 `BYTEDCLI_LIFE_COOKIE`

输出：

- JSON 模式返回 `metrics`、`meta`、`rows`、`extra`
- `metrics` 是接口原始指标字典
- `meta` 是指标元数据，包含分组、默认展示、类型和帮助文案
- `rows` 是 CLI 归一后的展示行，处理了 `data` 外层 key、内层 `key` 与 `meta.dataIndex` 不一致的情况
- `extra.supply_diagnosis_desc` 是后端诊断文案

展示规则：

- 文本模式默认只展示 `meta.extra.default=true` 的指标
- `self_compare` 是 ratio，例如 `-0.25` 展示为 `-25.00%`
- `unit: "%"` 的 `value` 已经是百分数
- `self_avg` 或 `self_compare` 为 `--` 时表示无对照值
