---
name: aime-skill
description: Aime (aime.tiktok-row.net) 自动化操作技能。支持任务创建、查询、结果获取等操作。触发词：aime、任务创建、任务查询、aime 登录、aime 操作。当用户提到 aime、创建任务、查询任务、获取任务结果、飞书文档生成等操作时，都应该使用此 skill。
allowed-tools: Bash(NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest auth:*), Bash(curl *)
---

# Aime Automation Skill

Aime (aime.tiktok-row.net) 自动化操作技能，通过纯 API 调用实现任务创建、查询、结果获取等功能。

## 核心原则

- ✅ **纯 API 调用** - 无需浏览器，使用 curl 直接调用
- ✅ **稳定高效** - 不受 UI 变化影响，响应快速
- ✅ **Session 持久化** - 通过 JWT token 保持登录态

## 前置条件

### SSO 认证

```bash
# 获取 bytecloud JWT token（必须使用 --site i18n-tt）
JWT=$(NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest --site i18n-tt auth get-bytecloud-jwt-token)
```

## API 调用方式

### 认证机制

Aime API 需要两种认证信息：

1. **Cookie**: `bd_sso_3b6da9=<JWT Token>`
2. **Authorization Header**: `Byte-Cloud-JWT <JWT Token>`

### 快速开始

```bash
# 1. 获取 JWT Token
JWT=$(NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest --site i18n-tt auth get-bytecloud-jwt-token)

# 2. 获取工作空间列表
curl -s "https://aime.tiktok-row.net/api/agents/v2/user/list/space?limit=20" \
  -H "Content-Type: application/json" \
  -H "authorization: Byte-Cloud-JWT ${JWT}" \
  -H "cookie: bd_sso_3b6da9=${JWT}" | jq '.'

# 3. 创建任务（封装为函数）
create_aime_task() {
  local content="$1"
  local space_id="${2:-c8cf4ea8-07c9-4082-8cad-ea98bf0ac626}"  # 默认使用 TikTok Lite 团队空间
  local mode_type="${3:-auto}"
  local jwt=$(NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest --site i18n-tt auth get-bytecloud-jwt-token)
  
  # 创建 Session
  local session_resp=$(curl -s "https://aime.tiktok-row.net/api/agents/v2/sessions" \
    -X POST \
    -H "Content-Type: application/json" \
    -H "authorization: Byte-Cloud-JWT ${jwt}" \
    -H "cookie: bd_sso_3b6da9=${jwt}" \
    -d "{\"role\":3,\"use_internal_tool\":true,\"space_id\":\"${space_id}\",\"excluded_mcps\":[]}")
  
  local session_id=$(echo "$session_resp" | jq -r '.session.id')
  echo "Session 创建成功：$session_id"
  
  # 发送任务消息
  curl -s "https://aime.tiktok-row.net/api/agents/v2/sessions/${session_id}/message" \
    -X POST \
    -H "Content-Type: application/json" \
    -H "authorization: Byte-Cloud-JWT ${jwt}" \
    -H "cookie: bd_sso_3b6da9=${jwt}" \
    -d "{\"content\":\"${content}\",\"attachments\":[],\"event_offset\":0,\"options\":\"{\\\"locale\\\":\\\"zh\\\"}\",\"mentions\":[],\"space_id\":\"${space_id}\",\"mode_type\":\"${mode_type}\"}"
}

# 4. 使用示例
create_aime_task "请介绍一下 Python 语言的特点"
```

### 获取工作空间列表

每个任务都需要指定一个工作空间。

```bash
JWT=$(NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest --site i18n-tt auth get-bytecloud-jwt-token)

curl -s "https://aime.tiktok-row.net/api/agents/v2/user/list/space?limit=20" \
  -H "Content-Type: application/json" \
  -H "authorization: Byte-Cloud-JWT ${JWT}" \
  -H "cookie: bd_sso_3b6da9=${JWT}" | jq '.spaces[] | {id, name, type}'
```

**响应示例**：
```json
{
  "id": "c8cf4ea8-07c9-4082-8cad-ea98bf0ac626",
  "name": "TikTok Lite",
  "type": "project"
}
```

**默认工作空间**：默认使用 TikTok Lite 团队空间 (`c8cf4ea8-07c9-4082-8cad-ea98bf0ac626`)。如需指定其他工作空间，传入 `space_id` 参数即可。

### 创建任务（完整示例）

```bash
JWT=$(NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest --site i18n-tt auth get-bytecloud-jwt-token)
SPACE_ID="c8cf4ea8-07c9-4082-8cad-ea98bf0ac626"

# 步骤 1：创建 Session
SESSION_RESP=$(curl -s "https://aime.tiktok-row.net/api/agents/v2/sessions" \
  -X POST \
  -H "Content-Type: application/json" \
  -H "authorization: Byte-Cloud-JWT ${JWT}" \
  -H "cookie: bd_sso_3b6da9=${JWT}" \
  -d "{\"role\":3,\"use_internal_tool\":true,\"space_id\":\"${SPACE_ID}\",\"excluded_mcps\":[]}")

SESSION_ID=$(echo "$SESSION_RESP" | jq -r '.session.id')
echo "Session ID: $SESSION_ID"

# 步骤 2：发送任务消息
curl -s "https://aime.tiktok-row.net/api/agents/v2/sessions/${SESSION_ID}/message" \
  -X POST \
  -H "Content-Type: application/json" \
  -H "authorization: Byte-Cloud-JWT ${JWT}" \
  -H "cookie: bd_sso_3b6da9=${JWT}" \
  -d "{\"content\":\"用一句话介绍 Python\",\"attachments\":[],\"event_offset\":0,\"options\":\"{\\\"locale\\\":\\\"zh\\\"}\",\"mentions\":[],\"space_id\":\"${SPACE_ID}\",\"mode_type\":\"auto\"}" | jq '.'
```

### 查询任务列表

```bash
SPACE_ID="c8cf4ea8-07c9-4082-8cad-ea98bf0ac626"

curl -s "https://aime.tiktok-row.net/api/agents/v3/sessions?space_id=${SPACE_ID}&limit=10&next_id=" \
  -H "authorization: Byte-Cloud-JWT ${JWT}" \
  -H "cookie: bd_sso_3b6da9=${JWT}" | jq '.sessions[:5] | .[] | {id, title, status, created_at}'
```

### 获取任务详情

```bash
SESSION_ID="0b5f1851-7d60-4653-a0e7-754afd458d34"

curl -s "https://aime.tiktok-row.net/api/agents/v2/sessions/${SESSION_ID}?space_id=${SPACE_ID}" \
  -H "authorization: Byte-Cloud-JWT ${JWT}" \
  -H "cookie: bd_sso_3b6da9=${JWT}" | jq '.session | {id, title, status, created_at}'
```

### 持续监控任务状态

如需持续监控任务是否完成或中途停止，使用获取任务详情的接口，通过判断返回的 `status` 字段得到结论。轮询间隔建议在 30s 以上：

```bash
# 使用脚本函数（推荐）
source scripts/aime-api.sh
watch_task_curl "0b5f1851-7d60-4653-a0e7-754afd458d34" "" 30

# 或手动实现轮询逻辑
SESSION_ID="0b5f1851-7d60-4653-a0e7-754afd458d34"
JWT=$(NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest --site i18n-tt auth get-bytecloud-jwt-token)

while true; do
  status=$(curl -s "https://aime.tiktok-row.net/api/agents/v2/sessions/${SESSION_ID}?space_id=${SPACE_ID}" \
    -H "authorization: Byte-Cloud-JWT ${JWT}" \
    -H "cookie: bd_sso_3b6da9=${JWT}" | jq -r '.session.status')
  
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] 任务状态：$status"
  
  case "$status" in
    "idle"|"closed"|"stopped")
      echo "任务已完成/停止"
      break
      ;;
    *)
      sleep 30  # 轮询间隔 30 秒
      ;;
  esac
done
```

**任务状态说明**：

| status | 说明 |
|--------|------|
| `created` | 已创建 |
| `waiting` | 等待中 |
| `running` | 执行中 |
| `idle` | 空闲（已完成） |
| `stopped` | 已停止 |
| `closed` | 已关闭 |

### 获取任务历史事件

```bash
SESSION_ID="0b5f1851-7d60-4653-a0e7-754afd458d34"

curl -s "https://aime.tiktok-row.net/api/agents/v2/sessions/${SESSION_ID}/old_events?space_id=${SPACE_ID}" \
  -H "authorization: Byte-Cloud-JWT ${JWT}" \
  -H "cookie: bd_sso_3b6da9=${JWT}" | jq '.events[:5] | .[] | {event, role: .data.message.role, content: .data.message.content[:200]}'
```

### 获取飞书文档列表

```bash
SESSION_ID="0b5f1851-7d60-4653-a0e7-754afd458d34"

curl -s "https://aime.tiktok-row.net/api/agents/v2/lark_doc/comments?session_id=${SESSION_ID}&aime_comment_text=%40Aime%20%E5%9C%A8%E5%9B%9E%E5%A4%8D%E4%B8%AD%E8%BE%93%E5%85%A5%E8%AF%89%E6%B1%82&space_id=${SPACE_ID}" \
  -H "authorization: Byte-Cloud-JWT ${JWT}" \
  -H "cookie: bd_sso_3b6da9=${JWT}" | jq '.lark_doc_comments[] | {name, url: .lark_doc_url}'
```

### 任务模式

| mode_type | 说明 |
|-----------|------|
| `auto` | 自动模式（推荐） |
| `ask` | 问答模式 |
| `agent` | Agent 模式 |

## 辅助脚本

可以使用 `scripts/aime-api.sh` 中的封装函数（纯 curl 版本）：

```bash
source scripts/aime-api.sh

# 获取工作空间列表
list_spaces_curl

# 创建任务
create_task_curl "请介绍一下 Python 语言的特点"

# 查询任务列表
list_tasks_curl "" 20 "搜索关键词"

# 获取任务执行结果（包含任务信息 + AI 回复 + 飞书文档）⭐
get_task_result_curl "session_id"

# 持续监控任务状态（轮询方式）⭐
watch_task_curl "session_id"
```

### 脚本函数说明

| 函数 | 说明 |
|------|------|
| `list_spaces_curl [limit]` | 获取工作空间列表 |
| `create_session_curl [space_id]` | 创建 Session |
| `send_message_curl <session_id> <content> [mode] [space_id]` | 发送任务消息 |
| `create_task_curl <content> [mode] [space_id]` | 一键创建任务 |
| `list_tasks_curl [space_id] [limit] [keyword]` | 查询任务列表 |
| `get_task_result_curl <session_id> [space_id] [count]` | 获取任务完整结果 |
| `watch_task_curl <session_id> [space_id] [interval]` | 持续监控任务状态（轮询间隔建议≥30s） |

## 错误处理

### 常见错误

| 错误 | 解决方案 |
|------|---------|
| `{"code": 401, "message": "unauthorized"}` | JWT token 过期，重新获取 |
| `Failed to fetch` | 网络问题或 API 地址错误 |
| `{"code": 403}` | 无权限访问该工作空间 |

### 调试技巧

```bash
# 检查 JWT 是否有效
JWT=$(NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest --site i18n-tt auth get-bytecloud-jwt-token)
echo "JWT: ${JWT:0:50}..."

# 测试 API 连通性
curl -s "https://aime.tiktok-row.net/api/agents/v2/user/list/space?limit=1" \
  -H "authorization: Byte-Cloud-JWT ${JWT}" \
  -H "cookie: bd_sso_3b6da9=${JWT}" | jq '.'
```

## 更多资源

- **API 规范**：`references/api-specification.md` - 完整的 API 文档
- **API 辅助脚本**：`scripts/aime-api.sh` - 常用 API 调用封装函数
- **故障排除**：`references/troubleshooting.md` - 常见问题解决

## 总结

| 场景 | API 端点 |
|------|---------|
| 创建任务 | `POST /api/agents/v2/sessions` + `POST /api/agents/v2/sessions/{id}/message` |
| 查询任务列表 | `GET /api/agents/v3/sessions?space_id={id}` |
| 获取任务详情 | `GET /api/agents/v2/sessions/{id}` |
| 获取历史事件 | `GET /api/agents/v2/sessions/{id}/old_events` |
| 获取飞书文档 | `GET /api/agents/v2/lark_doc/comments?session_id={id}` |
