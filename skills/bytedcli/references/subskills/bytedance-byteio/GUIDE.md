---
name: bytedance-byteio
description: "Operate ByteIO via bytedcli: query event schema/detail, check event parameters, list and inspect requirements, BTM points, test cases, location attributes, location events, ad tags/labels, and events by owner email prefix. Use when tasks mention ByteIO, 埋点, event tracking, event_name, schema/detail, 需求, 点位, BTM, 测试用例, 广告 tag/label, or need to verify whether an app_id + event_name exists."
---

# bytedcli ByteIO

Use this skill for ByteIO event tracking metadata and governance queries.

## When to use

- 用户要确认某个埋点、事件名或 `event_name` 是否存在，或查看单个埋点元数据详情
- 用户要校验埋点参数是否匹配 ByteIO schema
- 用户要查询 ByteIO 需求列表、需求详情、需求中的点位列表
- 用户要查询 BTM 点位详情、业务线下点位、点位上的埋点
- 用户要查询测试用例信息列表、测试用例详情
- 用户要查询广告 tag / label，或按用户邮箱前缀查询埋点信息

## Authentication

ByteIO OpenAPI requires an `authorization` header. Configure it through an environment variable before running commands:

```bash
export BYTEDCLI_BYTEIO_AUTHORIZATION=<byteio-openapi-authorization>
```

Do not print or persist the authorization value in summaries, docs, fixtures, or examples.

## Common options

- `--region cn|sg`: ByteIO OpenAPI region. Default: `cn`.
- `--body-json <json>`: supported by POST commands to merge extra request body fields from the API document.
- `--json`: global bytedcli flag. Put it before the command, for example `bytedcli --json byteio event get ...`.

## Command map

```bash
# 查询单个埋点元数据详情
bytedcli byteio event get --app-id 123 --event-name demo_event
bytedcli byteio event get --app-id 123 --event-name demo_event --include-scene

# 校验埋点参数
bytedcli byteio event check-params \
  --app-id-list 123 \
  --event-name-list demo_event \
  --param-name-list demo_param

bytedcli byteio event check-params \
  --checks-json '[{"app_id_list":[123],"event_name_list":["demo_event"],"param_name_list":["*"]}]'

# 根据用户邮箱前缀查询埋点信息
bytedcli byteio event list --owner demo.user

# 查询需求列表 / 详情 / 需求中的点位列表
bytedcli byteio requirement list --app-id 123 --keyword demo --page 1 --page-size 50
bytedcli byteio requirement get --requirement-id 456
bytedcli byteio requirement locations --app-id 123 --requirement-id 456

# 查询 BTM 点位详情
bytedcli byteio btm point get --operator demo.user --requirement-id 456
bytedcli byteio btm point get --operator demo.user --requirement-id 456 --btm-full-code-list demo.point

# 查询测试用例信息列表 / 详情
bytedcli byteio test-case list --app-id 123 --event-name demo_event --page 1 --page-size 20
bytedcli byteio test-case get --test-case-id demo-case-id

# 根据业务线查询点位；根据点位查询点位上的埋点
bytedcli byteio map locations --app-id 123 --business-module-ids 1,2
bytedcli byteio map events --app-id 123 --full-identifier-list demo.page.button

# 查询广告 tag / label
bytedcli byteio ad tags
bytedcli byteio ad labels
```

## Existence checks

For "埋点是否存在" tasks, prefer:

```bash
bytedcli --json byteio event get --app-id 123 --event-name demo_event
```

Interpretation:

- `exists: true`: request succeeds and the response contains non-empty schema/detail data.
- `exists: false`: response clearly indicates empty data or not found.
- `exists: unknown`: authorization, permission, network, timeout, non-JSON, or unclear business errors.

Always report `app_id`, `event_name`, existence, and concise response evidence. Do not include the authorization value.

## References

- `references/byteio.md`
- `references/invocation.md`
- `references/troubleshooting.md`
