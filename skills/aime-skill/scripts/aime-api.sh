#!/bin/bash

# Aime API 辅助脚本（纯 curl 版本）
# 用于直接调用 Aime API，无需浏览器

set -e

# ============================================================================
# 基础函数
# ============================================================================

# 获取 JWT Token
get_jwt_token() {
    NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest --site i18n-tt auth get-bytecloud-jwt-token 2>/dev/null
}

# ============================================================================
# 纯 curl API 调用函数（推荐）
# ============================================================================

# 获取工作空间列表（curl 版本）
list_spaces_curl() {
    local limit="${1:-20}"
    local jwt=$(get_jwt_token)
    
    curl -s "https://aime.tiktok-row.net/api/agents/v2/user/list/space?limit=${limit}" \
      -H "Content-Type: application/json" \
      -H "authorization: Byte-Cloud-JWT ${jwt}" \
      -H "cookie: bd_sso_3b6da9=${jwt}" | jq '.'
}

# 创建 Session（curl 版本）
create_session_curl() {
    local space_id="${1:-c8cf4ea8-07c9-4082-8cad-ea98bf0ac626}"  # 默认使用 TikTok Lite 团队空间
    local jwt=$(get_jwt_token)
    
    curl -s "https://aime.tiktok-row.net/api/agents/v2/sessions" \
      -X POST \
      -H "Content-Type: application/json" \
      -H "authorization: Byte-Cloud-JWT ${jwt}" \
      -H "cookie: bd_sso_3b6da9=${jwt}" \
      -d "{\"role\":3,\"use_internal_tool\":true,\"space_id\":\"${space_id}\",\"excluded_mcps\":[]}" | jq '.'
}

# 发送消息（curl 版本）
send_message_curl() {
    local session_id="$1"
    local content="$2"
    local mode_type="${3:-auto}"
    local space_id="${4:-c8cf4ea8-07c9-4082-8cad-ea98bf0ac626}"  # 默认使用 TikTok Lite 团队空间
    local jwt=$(get_jwt_token)
    
    curl -s "https://aime.tiktok-row.net/api/agents/v2/sessions/${session_id}/message" \
      -X POST \
      -H "Content-Type: application/json" \
      -H "authorization: Byte-Cloud-JWT ${jwt}" \
      -H "cookie: bd_sso_3b6da9=${jwt}" \
      -d "{\"content\":\"${content}\",\"attachments\":[],\"event_offset\":0,\"options\":\"{\\\"locale\\\":\\\"zh\\\"}\",\"mentions\":[],\"space_id\":\"${space_id}\",\"mode_type\":\"${mode_type}\"}" | jq '.'
}

# 创建任务（curl 版本，一步完成）
create_task_curl() {
    local content="$1"
    local mode_type="${2:-auto}"
    local space_id="${3:-c8cf4ea8-07c9-4082-8cad-ea98bf0ac626}"  # 默认使用 TikTok Lite 团队空间
    local jwt=$(get_jwt_token)
    
    echo "正在创建任务..."
    
    # 创建 session
    local session_result=$(curl -s "https://aime.tiktok-row.net/api/agents/v2/sessions" \
      -X POST \
      -H "Content-Type: application/json" \
      -H "authorization: Byte-Cloud-JWT ${jwt}" \
      -H "cookie: bd_sso_3b6da9=${jwt}" \
      -d "{\"role\":3,\"use_internal_tool\":true,\"space_id\":\"${space_id}\",\"excluded_mcps\":[]}")
    
    local session_id=$(echo "$session_result" | jq -r '.session.id')
    
    if [ -z "$session_id" ] || [ "$session_id" = "null" ]; then
        echo "创建 session 失败：$session_result"
        return 1
    fi
    
    echo "Session 创建成功：$session_id"
    
    # 发送消息
    local message_result=$(curl -s "https://aime.tiktok-row.net/api/agents/v2/sessions/${session_id}/message" \
      -X POST \
      -H "Content-Type: application/json" \
      -H "authorization: Byte-Cloud-JWT ${jwt}" \
      -H "cookie: bd_sso_3b6da9=${jwt}" \
      -d "{\"content\":\"${content}\",\"attachments\":[],\"event_offset\":0,\"options\":\"{\\\"locale\\\":\\\"zh\\\"}\",\"mentions\":[],\"space_id\":\"${space_id}\",\"mode_type\":\"${mode_type}\"}")
    
    echo "任务提交结果:"
    echo "$message_result"
    echo ""
    echo "任务 ID: $session_id"
}

# 查询任务列表（curl 版本）
list_tasks_curl() {
    local space_id="${1:-c8cf4ea8-07c9-4082-8cad-ea98bf0ac626}"  # 默认使用 TikTok Lite 团队空间
    local limit="${2:-20}"
    local search_keyword="${3:-}"
    local jwt=$(get_jwt_token)
    
    # URL 编码搜索关键词
    local encoded_search=""
    if [ -n "$search_keyword" ]; then
        encoded_search=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$search_keyword'))" 2>/dev/null || echo "$search_keyword")
    fi
    
    curl -s "https://aime.tiktok-row.net/api/agents/v3/sessions?space_id=${space_id}&limit=${limit}&next_id=&search=${encoded_search}&trigger_task_id=" \
      -H "authorization: Byte-Cloud-JWT ${jwt}" \
      -H "cookie: bd_sso_3b6da9=${jwt}" | jq '.'
}

# 获取任务详情（curl 版本）
get_task_curl() {
    local session_id="$1"
    local space_id="${2:-c8cf4ea8-07c9-4082-8cad-ea98bf0ac626}"
    local jwt=$(get_jwt_token)
    
    curl -s "https://aime.tiktok-row.net/api/agents/v2/sessions/${session_id}?space_id=${space_id}" \
      -H "authorization: Byte-Cloud-JWT ${jwt}" \
      -H "cookie: bd_sso_3b6da9=${jwt}" | jq '.'
}

# 获取任务历史事件（curl 版本）
get_task_events_curl() {
    local session_id="$1"
    local space_id="${2:-c8cf4ea8-07c9-4082-8cad-ea98bf0ac626}"
    local limit="${3:-10}"
    local jwt=$(get_jwt_token)
    
    curl -s "https://aime.tiktok-row.net/api/agents/v2/sessions/${session_id}/old_events?space_id=${space_id}" \
      -H "authorization: Byte-Cloud-JWT ${jwt}" \
      -H "cookie: bd_sso_3b6da9=${jwt}" | \
      jq --argjson limit "$limit" '.events[:$limit] | .[] | {event, role: .data.message.role, content: .data.message.content[:300]}'
}

# 获取任务飞书文档（curl 版本）
get_task_docs_curl() {
    local session_id="$1"
    local space_id="${2:-c8cf4ea8-07c9-4082-8cad-ea98bf0ac626}"
    local jwt=$(get_jwt_token)
    
    curl -s "https://aime.tiktok-row.net/api/agents/v2/lark_doc/comments?session_id=${session_id}&aime_comment_text=%40Aime%20%E5%9C%A8%E5%9B%9E%E5%A4%8D%E4%B8%AD%E8%BE%93%E5%85%A5%E8%AF%89%E6%B1%82&space_id=${space_id}" \
      -H "authorization: Byte-Cloud-JWT ${jwt}" \
      -H "cookie: bd_sso_3b6da9=${jwt}" | \
      jq '.lark_doc_comments[]? | {name, url: .lark_doc_url}'
}

# 获取任务执行结果（curl 版本，推荐）⭐
# 组合：任务信息 + 最后几次 AI 回复 + 飞书文档
get_task_result_curl() {
    local session_id="$1"
    local space_id="${2:-c8cf4ea8-07c9-4082-8cad-ea98bf0ac626}"  # 默认使用 TikTok Lite 团队空间
    local event_count="${3:-5}"
    local jwt=$(get_jwt_token)
    
    echo "=== 任务基本信息 ==="
    local session_resp=$(curl -s "https://aime.tiktok-row.net/api/agents/v2/sessions/${session_id}?space_id=${space_id}" \
      -H "authorization: Byte-Cloud-JWT ${jwt}" \
      -H "cookie: bd_sso_3b6da9=${jwt}")
    
    echo "$session_resp" | jq '.session | {id, title, status, created_at, creator}'
    
    echo -e "\n=== AI 回复（最近 ${event_count} 条）==="
    curl -s "https://aime.tiktok-row.net/api/agents/v2/sessions/${session_id}/old_events?space_id=${space_id}" \
      -H "authorization: Byte-Cloud-JWT ${jwt}" \
      -H "cookie: bd_sso_3b6da9=${jwt}" | \
      jq --argjson count "$event_count" \
         '[.events[] | select(.event == "session.message.create" and .data.message.role == "assistant")] | .[-$count:] | .[] | {created_at, content: .data.message.content[:500]}'
    
    echo -e "\n=== 飞书文档 ==="
    curl -s "https://aime.tiktok-row.net/api/agents/v2/lark_doc/comments?session_id=${session_id}&aime_comment_text=%40Aime%20%E5%9C%A8%E5%9B%9E%E5%A4%8D%E4%B8%AD%E8%BE%93%E5%85%A5%E8%AF%89%E6%B1%82&space_id=${space_id}" \
      -H "authorization: Byte-Cloud-JWT ${jwt}" \
      -H "cookie: bd_sso_3b6da9=${jwt}" | \
      jq '.lark_doc_comments[]? | {name, url: .lark_doc_url}'
}

# 持续监控任务状态（轮询方式）⭐
# 通过获取任务详情接口持续监控任务状态，轮询间隔 30s
watch_task_curl() {
    local session_id="$1"
    local space_id="${2:-c8cf4ea8-07c9-4082-8cad-ea98bf0ac626}"  # 默认使用 TikTok Lite 团队空间
    local interval="${3:-30}"  # 轮询间隔，默认 30 秒
    local jwt=$(get_jwt_token)
    
    echo "开始监控任务：$session_id"
    echo "轮询间隔：${interval}秒"
    echo "按 Ctrl+C 停止监控"
    echo ""
    
    while true; do
        local session_resp=$(curl -s "https://aime.tiktok-row.net/api/agents/v2/sessions/${session_id}?space_id=${space_id}" \
          -H "authorization: Byte-Cloud-JWT ${jwt}" \
          -H "cookie: bd_sso_3b6da9=${jwt}")
        
        local task_status=$(echo "$session_resp" | jq -r '.session.status')
        local title=$(echo "$session_resp" | jq -r '.session.title')
        local created_at=$(echo "$session_resp" | jq -r '.session.created_at')
        
        local current_time=$(date +"%Y-%m-%d %H:%M:%S")
        echo "[${current_time}] 任务状态：${task_status}"
        
        case "$task_status" in
            "created"|"waiting"|"running")
                echo "  任务正在执行中..."
                sleep "$interval"
                ;;
            "idle"|"closed")
                echo "  任务已完成"
                echo ""
                echo "=== 任务完成 ==="
                echo "任务 ID: $session_id"
                echo "任务标题：$title"
                echo "创建时间：$created_at"
                echo "最终状态：$task_status"
                break
                ;;
            "stopped")
                echo "  任务已停止"
                echo ""
                echo "=== 任务停止 ==="
                echo "任务 ID: $session_id"
                echo "任务标题：$title"
                echo "创建时间：$created_at"
                echo "最终状态：$task_status"
                break
                ;;
            *)
                echo "  未知状态：$task_status"
                sleep "$interval"
                ;;
        esac
    done
}

# ============================================================================
# 帮助信息
# ============================================================================

show_help() {
    cat <<EOF
Aime API 辅助脚本（纯 curl 版本）

用法:
    source aime-api.sh

函数列表:
    # 获取工作空间列表
    list_spaces_curl [limit]
    
    # 创建 Session
    create_session_curl [space_id]
    
    # 发送消息
    send_message_curl <session_id> <content> [mode_type] [space_id]
    
    # 创建任务（一键完成）⭐
    create_task_curl <content> [mode_type] [space_id]
    
    # 查询任务列表
    list_tasks_curl [space_id] [limit] [search_keyword]
    
    # 获取任务详情
    get_task_curl <session_id> [space_id]
    
    # 获取任务历史事件
    get_task_events_curl <session_id> [space_id] [limit]
    
    # 获取任务飞书文档
    get_task_docs_curl <session_id> [space_id]
    
    # 获取任务执行结果（推荐）⭐
    get_task_result_curl <session_id> [space_id] [event_count]
    
    # 持续监控任务状态（轮询）⭐
    watch_task_curl <session_id> [space_id] [interval]

参数说明:
    mode_type: auto | ask | agent (默认：auto)
    space_id: 工作空间 ID (默认：c8cf4ea8-07c9-4082-8cad-ea98bf0ac626 TikTok Lite)
    session_id: 任务 Session ID
    search_keyword: 搜索关键词（可选）
    limit: 返回数量限制（默认：20）
    event_count: 显示最后 N 条 AI 回复（默认：5）

示例:
    # 获取所有工作空间
    list_spaces_curl
    
    # 创建自动模式任务
    create_task_curl "请介绍一下 Python 语言的特点"
    
    # 查询最近 20 个任务
    list_tasks_curl
    
    # 搜索包含 "Python" 的任务
    list_tasks_curl "" 20 "Python"
    
    # 获取任务执行结果
    get_task_result_curl "270ef5f0-e019-4f3b-9cdc-96e8127a9e51"
    
    # 获取任务执行结果（显示最后 10 条 AI 回复）
    get_task_result_curl "270ef5f0-e019-4f3b-9cdc-96e8127a9e51" "" 10
    
    # 持续监控任务状态（每 30 秒轮询一次）
    watch_task_curl "270ef5f0-e019-4f3b-9cdc-96e8127a9e51"
    
    # 持续监控任务状态（自定义轮询间隔为 60 秒）
    watch_task_curl "270ef5f0-e019-4f3b-9cdc-96e8127a9e51" "" 60

EOF
}

# 主入口
if [ "$1" = "help" ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help
fi
