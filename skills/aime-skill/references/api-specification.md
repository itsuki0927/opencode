# Aime API 规范文档

## 概述

Aime 使用两阶段 API 调用流程来创建和提交任务：
1. 创建 Session（任务容器）
2. 发送 Message（任务内容）

## 认证机制

### 关键认证信息

Aime API 需要两种认证信息：

1. **Cookie**: `bd_sso_3b6da9=<JWT Token>`
   - 通过 bytedcli 获取
   - 每个请求都必须携带

2. **Authorization Header**: `Byte-Cloud-JWT <JWT Token>`
   - 每个 API 请求都必须包含此 header

### 获取认证信息

```bash
# 通过 bytedcli 获取 JWT Token
JWT=$(NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest --site i18n-tt auth get-bytecloud-jwt-token)
```

## API 端点

### 1. 获取工作空间列表

**请求**：
```http
GET https://aime.tiktok-row.net/api/agents/v2/user/list/space?limit=20
```

**Headers**：
```json
{
  "Content-Type": "application/json",
  "authorization": "Byte-Cloud-JWT <JWT>",
  "cookie": "bd_sso_3b6da9=<JWT>"
}
```

**响应**：
```json
{
  "spaces": [
    {
      "id": "c8cf4ea8-07c9-4082-8cad-ea98bf0ac626",
      "name": "TikTok Lite",
      "name_en": "TikTok Lite",
      "type": "project",
      "status": "active",
      "creator": "wangjinkai.mike",
      "created_at": "2026-01-16T07:57:00Z"
    },
    {
      "id": "675661a2-0668-4771-9611-f3fd3b7a31c2",
      "name": "王晋开 的工作空间",
      "name_en": "Jaxon's Workspace",
      "type": "personal",
      "status": "active",
      "creator": "wangjinkai.mike",
      "created_at": "2025-08-27T06:41:57Z"
    }
  ]
}
```

### 2. 创建 Session

**请求**：
```http
POST https://aime.tiktok-row.net/api/agents/v2/sessions
```

**Headers**：
```json
{
  "Content-Type": "application/json",
  "authorization": "Byte-Cloud-JWT <JWT>",
  "cookie": "bd_sso_3b6da9=<JWT>"
}
```

**Body**：
```json
{
  "role": 3,
  "use_internal_tool": true,
  "space_id": "c8cf4ea8-07c9-4082-8cad-ea98bf0ac626",
  "excluded_mcps": []
}
```

**参数说明**：
- `role`: 用户角色（3 = 普通用户）
- `use_internal_tool`: 是否使用内部工具（true）
- `space_id`: 工作空间 ID
- `excluded_mcps`: 排除的 MCP 列表（通常为空数组）

**响应**：
```json
{
  "session": {
    "id": "cafbf7ff-9b3b-4308-b0ab-9f738e6d8c4b",
    "status": "created",
    "title": "",
    "creator": "wangjinkai.mike",
    "created_at": "2026-03-11T03:49:29Z",
    "role": 3,
    "space_id": "c8cf4ea8-07c9-4082-8cad-ea98bf0ac626"
  }
}
```

### 3. 发送任务消息

**请求**：
```http
POST https://aime.tiktok-row.net/api/agents/v2/sessions/{session_id}/message
```

**Headers**：
```json
{
  "Content-Type": "application/json",
  "authorization": "Byte-Cloud-JWT <JWT>",
  "cookie": "bd_sso_3b6da9=<JWT>"
}
```

**Body**：
```json
{
  "content": "用一句话介绍 Python",
  "attachments": [],
  "event_offset": 0,
  "options": "{\"locale\":\"zh\"}",
  "mentions": [],
  "space_id": "c8cf4ea8-07c9-4082-8cad-ea98bf0ac626",
  "mode_type": "auto"
}
```

**参数说明**：
- `content`: 任务内容
- `attachments`: 附件列表（通常为空）
- `event_offset`: 事件偏移量（通常为 0）
- `options`: 选项 JSON 字符串，包含 locale
- `mentions`: 提及列表（通常为空）
- `space_id`: 工作空间 ID
- `mode_type`: 任务模式（auto/ask/agent）

**响应**：
```json
{
  "message": {
    "message_id": "8073c2d7-3fd8-47fd-9a71-4d2fd6e1aafc",
    "session_id": "cafbf7ff-9b3b-4308-b0ab-9f738e6d8c4b",
    "role": "user",
    "content": "用一句话介绍 Python",
    "creator": "wangjinkai.mike",
    "created_at": "2026-03-11T03:52:55Z",
    "mode_type": "auto"
  }
}
```

### 4. 查询任务列表

**请求**：
```http
GET https://aime.tiktok-row.net/api/agents/v3/sessions?space_id={space_id}&limit=20&next_id=&search={keyword}&trigger_task_id=
```

**Headers**：
```json
{
  "authorization": "Byte-Cloud-JWT <JWT>",
  "cookie": "bd_sso_3b6da9=<JWT>"
}
```

**响应**：
```json
{
  "sessions": [
    {
      "id": "54411eb1-bdd2-49be-8462-28f8b657962c",
      "title": "完成自己想出来的复杂任务",
      "status": "waiting",
      "created_at": "2026-03-10T12:48:34Z",
      "first_user_query": "任务内容"
    }
  ],
  "next_id": ""
}
```

### 5. 获取任务详情

**请求**：
```http
GET https://aime.tiktok-row.net/api/agents/v2/sessions/{session_id}?space_id={space_id}
```

**Headers**：
```json
{
  "authorization": "Byte-Cloud-JWT <JWT>",
  "cookie": "bd_sso_3b6da9=<JWT>"
}
```

**响应**：
```json
{
  "session": {
    "id": "54411eb1-bdd2-49be-8462-28f8b657962c",
    "title": "完成自己想出来的复杂任务",
    "status": "waiting",
    "created_at": "2026-03-10T12:48:34Z",
    "updated_at": "2026-03-10T12:48:34Z",
    "creator": "wangjinkai.mike",
    "first_user_query": "任务内容"
  }
}
```

### 6. 获取任务历史事件

**请求**：
```http
GET https://aime.tiktok-row.net/api/agents/v2/sessions/{session_id}/old_events?space_id={space_id}
```

**Headers**：
```json
{
  "authorization": "Byte-Cloud-JWT <JWT>",
  "cookie": "bd_sso_3b6da9=<JWT>"
}
```

**响应**：
```json
{
  "events": [
    {
      "event": "session.message.create",
      "data": {
        "message": {
          "role": "assistant",
          "content": "好的，我来帮你完成任务...",
          "created_at": "2026-03-10T12:48:40Z"
        }
      }
    }
  ]
}
```

### 7. 获取飞书文档列表

**请求**：
```http
GET https://aime.tiktok-row.net/api/agents/v2/lark_doc/comments?session_id={session_id}&aime_comment_text=%40Aime%20%E5%9C%A8%E5%9B%9E%E5%A4%8D%E4%B8%AD%E8%BE%93%E5%85%A5%E8%AF%89%E6%B1%82&space_id={space_id}
```

**Headers**：
```json
{
  "authorization": "Byte-Cloud-JWT <JWT>",
  "cookie": "bd_sso_3b6da9=<JWT>"
}
```

**响应**：
```json
{
  "lark_doc_comments": [
    {
      "artifact_id": "c9b0804f-5e1d-440b-ac80-a91c56fee71a",
      "name": "TikTok Lite 空间周度变更统计报告",
      "lark_doc_url": "https://bytedance.larkoffice.com/docx/KpHAdNILaoaMvMxePJPcvIbRnBf",
      "version": 1
    }
  ]
}
```

## 任务模式

| mode_type | 说明 |
|-----------|------|
| `auto` | 自动模式（推荐）- 自动匹配最佳处理方式 |
| `ask` | 问答模式 - 快速响应简单问题 |
| `agent` | Agent 模式 - 深度执行复杂任务 |

## 任务状态

| status | 说明 |
|--------|------|
| `created` | 已创建 |
| `waiting` | 等待中（任务刚创建，还未开始执行） |
| `running` | 执行中 |
| `idle` | 空闲（任务已完成） |
| `stopped` | 已停止（任务被手动停止） |
| `closed` | 已关闭 |

## 错误响应

### 401 Unauthorized
```json
{
  "code": 401,
  "message": "unauthorized"
}
```
**原因**：JWT token 过期或无效

### 403 Forbidden
```json
{
  "code": 403,
  "message": "forbidden"
}
```
**原因**：无权限访问该工作空间

### 500 Internal Server Error
```json
{
  "code": 500,
  "message": "internal server error"
}
```
**原因**：服务器内部错误
