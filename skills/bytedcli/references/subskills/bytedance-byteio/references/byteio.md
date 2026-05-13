# ByteIO

## Capability

ByteIO commands wrap the documented ByteIO OpenAPI surface for event tracking metadata, requirements, BTM points, test cases, location attributes, and ad metadata.

## Authentication

The OpenAPI gateway expects an `authorization` header. bytedcli reads it from:

1. `BYTEDCLI_BYTEIO_AUTHORIZATION`

Never hardcode real authorization values in repository files, test fixtures, skill docs, or user-facing summaries.

## Regions

| Region | OpenAPI base |
|--------|--------------|
| `cn` | `https://openapi-dp.byted.org/openapi/byteio-cn` |
| `sg` | `https://openapi-alisg.byted.org/openapi/byteio-sg` |

Use `--region cn|sg`; default is `cn`.

## Commands and APIs

| User task | Command | Method / path |
|-----------|---------|---------------|
| 查询单个埋点元数据详情 | `byteio event get --app-id <id> --event-name <name>` | `GET /byteio/open/v1/schema/detail` |
| 校验埋点参数 | `byteio event check-params --app-id-list <ids> --event-name-list <names> --param-name-list <names>` | `POST /byteio/open/v1/schema/param/check` |
| 查询需求列表 | `byteio requirement list --app-id <id>` | `POST /byteio/open/v1/requirements/list` |
| 查询需求详情 | `byteio requirement get --requirement-id <id>` | `GET /byteio/open/v1/requirements/{id}/` |
| 查询 BTM 点位详情 | `byteio btm point get --operator <user> --requirement-id <id>` | `POST /open/v1/btm_requirement/get_point_details` |
| 查询测试用例信息列表 | `byteio test-case list --app-id <id>` | `POST /open/v1/test_case_suite/test_case/info/list` |
| 查询测试用例详情 | `byteio test-case get --test-case-id <id>` | `GET /open/v1/test_case_suite/test_case/{test_case_id}` |
| 根据业务线查询点位 | `byteio map locations --app-id <id> --business-module-ids <ids>` | `POST /open/v1/event_map/location_attribute/tree` |
| 根据点位查询点位上的埋点 | `byteio map events --app-id <id> --full-identifier-list <ids>` | `POST /byteio/open/v1/event_map/location_attribute/group/event/list` |
| 查询需求中的点位列表 | `byteio requirement locations --app-id <id> --requirement-id <id>` | `POST /byteio/open/v1/event_map/location_attribute/list_in_requirement` |
| 查询广告 tag 列表 | `byteio ad tags` | `GET /open/v1/ad/data_manage/tag/list` |
| 查询广告 label 列表 | `byteio ad labels` | `GET /open/v1/ad/data_manage/label/list` |
| 根据用户邮箱前缀查询埋点信息 | `byteio event list --owner <owner>` | `POST /byteio/open/v1/schema/name/list` |

## Important parameters

- `event get`: `--app-id`, `--event-name`, optional `--include-scene`
- `event check-params`: either the three list flags or `--checks-json`; use `--param-name-list '*'` to check all params
- `requirement list`: `--app-id`; optional `--keyword`, `--owner`, `--requirement-status`, `--requirement-status-list`, `--requirement-id-list`, `--type`, `--external-rid`, `--page`, `--page-size`, `--filter-empty-location-attribute`
- `btm point get`: `--operator`, `--requirement-id`; optional `--btm-full-code-list`
- `test-case list`: `--app-id`; optional `--test-case-ids`, `--test-case-suite-ids`, `--name`, `--event-name`, `--page`, `--page-size`
- `map locations`: `--app-id`; optional `--business-module-ids` as comma-separated values or JSON array
- `map events`: `--app-id`, `--full-identifier-list`; optional `--event-trigger-type-list`, `--page`, `--page-size`

POST commands that have typed options also support `--body-json <json>` to merge additional documented fields into the request body.

## Response interpretation

For existence checks:

- `exists: true`: the HTTP request succeeds and the response has non-empty event schema/detail data.
- `exists: false`: the HTTP request succeeds and the response clearly indicates empty data or not found.
- `exists: "unknown"`: authorization, permission, network, timeout, invalid JSON, or unclear business errors.

Always include concise evidence: business code/message when present and whether a non-empty detail payload was returned.
