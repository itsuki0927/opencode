# Aime API 调用示例

本文档包含 aime-skill 的纯 API 调用示例。

## 目录

- [基础示例](#基础示例)
- [创建任务示例](#创建任务示例)
- [查询任务示例](#查询任务示例)
- [获取结果示例](#获取结果示例)

## 基础示例

### 获取 JWT Token

```bash
JWT=$(NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest --site i18n-tt auth get-bytecloud-jwt-token)
echo "JWT: ${JWT:0:50}..."
```

### 获取工作空间列表

```bash
JWT=$(NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest --site i18n-tt auth get-bytecloud-jwt-token)

curl -s "https://aime.tiktok-row.net/api/agents/v2/user/list/space?limit=20" \
  -H "authorization: Byte-Cloud-JWT ${JWT}" \
  -H "cookie: bd_sso_3b6da9=${JWT}" | jq '.spaces[] | {id, name, type}'
```

**输出**：
```json
{
  "id": "c8cf4ea8-07c9-4082-8cad-ea98bf0ac626",
  "name": "TikTok Lite",
  "type": "project"
}
{
  "id": "675661a2-0668-4771-9611-f3fd3b7a31c2",
  "name": "王晋开 的工作空间",
  "type": "personal"
}
```

## 创建任务示例

### 示例 1：简单任务（Auto 模式）

```bash
JWT=$(NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest --site i18n-tt auth get-bytecloud-jwt-token)
SPACE_ID="c8cf4ea8-07c9-4082-8cad-ea98bf0ac626"

# 创建 Session
SESSION_RESP=$(curl -s "https://aime.tiktok-row.net/api/agents/v2/sessions" \
  -X POST \
  -H "authorization: Byte-Cloud-JWT ${JWT}" \
  -H "cookie: bd_sso_3b6da9=${JWT}" \
  -H "Content-Type: application/json" \
  -d "{\"role\":3,\"use_internal_tool\":true,\"space_id\":\"${SPACE_ID}\",\"excluded_mcps\":[]}")

SESSION_ID=$(echo "$SESSION_RESP" | jq -r '.session.id')
echo "Session ID: $SESSION_ID"

# 发送消息
curl -s "https://aime.tiktok-row.net/api/agents/v2/sessions/${SESSION_ID}/message" \
  -X POST \
  -H "authorization: Byte-Cloud-JWT ${JWT}" \
  -H "cookie: bd_sso_3b6da9=${JWT}" \
  -H "Content-Type: application/json" \
  -d "{\"content\":\"用一句话介绍 Python\",\"space_id\":\"${SPACE_ID}\",\"mode_type\":\"auto\"}" | jq '.'
```

### 示例 2：使用辅助脚本（推荐）

```bash
# 加载脚本
source scripts/aime-api.sh

# 一键创建任务
create_task_curl "请介绍一下 Python 语言的特点"
```

### 示例 3：Agent 模式任务

```bash
source scripts/aime-api.sh

# 创建 Agent 模式任务
create_task_curl "帮我分析这个代码仓库的结构和主要功能" "agent"
```

### 示例 4：指定工作空间

```bash
source scripts/aime-api.sh

# 使用个人工作空间
create_task_curl "测试任务" "auto" "675661a2-0668-4771-9611-f3fd3b7a31c2"
```

## 查询任务示例

### 示例 1：查询任务列表

```bash
source scripts/aime-api.sh

# 查询最近 20 个任务
list_tasks_curl | jq '.sessions[:10] | .[] | {id, title, status}'
```

### 示例 2：搜索任务

```bash
source scripts/aime-api.sh

# 搜索包含 "Python" 的任务
list_tasks_curl "" 20 "Python" | jq '.sessions[] | {id, title}'
```

### 示例 3：获取任务详情

```bash
source scripts/aime-api.sh

# 获取任务详情
get_task_curl "270ef5f0-e019-4f3b-9cdc-96e8127a9e51" | jq '.session | {id, title, status, created_at}'
```

## 获取结果示例

### 示例 1：获取任务完整结果

```bash
source scripts/aime-api.sh

# 获取任务执行结果（包含任务信息 + AI 回复 + 飞书文档）
get_task_result_curl "270ef5f0-e019-4f3b-9cdc-96e8127a9e51"
```

**输出**：
```
=== 任务基本信息 ===
{
  "id": "270ef5f0-e019-4f3b-9cdc-96e8127a9e51",
  "title": "TikTok Lite 空间过去一周变更统计及季度趋势图",
  "status": "stopped",
  "created_at": "2026-03-10T15:03:25Z",
  "creator": "macheng.66"
}

=== AI 回复（最近 5 条）===
{...}

=== 飞书文档 ===
{
  "name": "TikTok Lite 空间周度变更统计报告 (2026-03-04 ~ 2026-03-10)",
  "url": "https://bytedance.larkoffice.com/docx/KpHAdNILaoaMvMxePJPcvIbRnBf"
}
```

### 示例 2：获取飞书文档列表

```bash
source scripts/aime-api.sh

# 获取任务关联的飞书文档
get_task_docs_curl "270ef5f0-e019-4f3b-9cdc-96e8127a9e51"
```

### 示例 3：获取历史事件

```bash
source scripts/aime-api.sh

# 获取任务历史事件（最近 10 条）
get_task_events_curl "270ef5f0-e019-4f3b-9cdc-96e8127a9e51" "" 10
```

## 完整工作流示例

```bash
#!/bin/bash

# 1. 加载脚本
source scripts/aime-api.sh

# 2. 创建工作空间
echo "=== 可用工作空间 ==="
list_spaces_curl | jq '.spaces[] | {id, name}'

# 3. 创建任务
echo -e "\n=== 创建任务 ==="
create_task_curl "统计 TikTok Lite 空间本周的变更情况"

# 4. 查询任务列表
echo -e "\n=== 最近任务 ==="
list_tasks_curl | jq '.sessions[:5] | .[] | {id, title, status}'

# 5. 获取特定任务结果
echo -e "\n=== 任务结果 ==="
get_task_result_curl "<session_id>"
```
