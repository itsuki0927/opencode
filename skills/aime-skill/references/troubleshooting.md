# Aime API 故障排除

本文档包含 aime-skill 的错误处理和故障排除指南。

## 目录

- [常见错误](#常见错误)
- [诊断工具](#诊断工具)
- [最佳实践](#最佳实践)

## 常见错误

### 1. 401 Unauthorized

**错误信息**：
```json
{"code": 401, "message": "unauthorized"}
```

**原因**：JWT token 过期或无效

**解决方案**：
```bash
# 重新获取 JWT token
JWT=$(NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest --site i18n-tt auth get-bytecloud-jwt-token)

# 测试 token 是否有效
curl -s "https://aime.tiktok-row.net/api/agents/v2/user/list/space?limit=1" \
  -H "authorization: Byte-Cloud-JWT ${JWT}" \
  -H "cookie: bd_sso_3b6da9=${JWT}"
```

### 2. 403 Forbidden

**错误信息**：
```json
{"code": 403, "message": "forbidden"}
```

**原因**：无权限访问该工作空间

**解决方案**：
```bash
# 检查可用的工作空间
JWT=$(NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest --site i18n-tt auth get-bytecloud-jwt-token)

curl -s "https://aime.tiktok-row.net/api/agents/v2/user/list/space?limit=20" \
  -H "authorization: Byte-Cloud-JWT ${JWT}" \
  -H "cookie: bd_sso_3b6da9=${JWT}" | jq '.spaces[] | {id, name, type}'

# 使用有权限的工作空间
```

### 3. 连接失败

**错误信息**：
```
Failed to fetch
curl: (6) Could not resolve host
```

**原因**：网络连接问题

**解决方案**：
```bash
# 检查网络连通性
curl -I https://aime.tiktok-row.net

# 检查 DNS 解析
ping aime.tiktok-row.net
```

### 4. Session 创建失败

**错误信息**：
```json
{"code": 500, "message": "internal server error"}
```

**原因**：服务器内部错误或参数错误

**解决方案**：
```bash
# 检查 space_id 是否正确
# 确保 space_id 是有效的 UUID 格式

# 重试创建
create_session_curl "c8cf4ea8-07c9-4082-8cad-ea98bf0ac626"
```

### 5. jq 解析错误

**错误信息**：
```
jq: parse error: Invalid JSON
```

**原因**：API 返回的不是 JSON 格式

**解决方案**：
```bash
# 先检查原始响应
curl -s "..." -H "..." | head

# 确认响应是 JSON 格式后再用 jq 解析
```

## 诊断工具

### 检查 JWT Token

```bash
# 获取 JWT
JWT=$(NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest --site i18n-tt auth get-bytecloud-jwt-token)

# 显示前 50 个字符（用于确认）
echo "JWT: ${JWT:0:50}..."

# 检查 JWT 格式（应该是有效的 JWT，包含两个点号）
echo "$JWT" | grep -q "^\ ey.*\..*\." && echo "JWT 格式正确" || echo "JWT 格式错误"
```

### 测试 API 连通性

```bash
JWT=$(NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest --site i18n-tt auth get-bytecloud-jwt-token)

# 测试获取工作空间
curl -s -w "\nHTTP Status: %{http_code}\n" \
  "https://aime.tiktok-row.net/api/agents/v2/user/list/space?limit=1" \
  -H "authorization: Byte-Cloud-JWT ${JWT}" \
  -H "cookie: bd_sso_3b6da9=${JWT}"
```

### 调试脚本

```bash
debug_aime_api() {
    echo "=== Aime API 诊断 ==="
    
    # 1. 检查 JWT
    echo -e "\n1. JWT Token 检查"
    JWT=$(NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest --site i18n-tt auth get-bytecloud-jwt-token 2>/dev/null)
    if [ -n "$JWT" ]; then
        echo "✓ JWT 获取成功"
        echo "  前缀：${JWT:0:30}..."
    else
        echo "✗ JWT 获取失败"
        return 1
    fi
    
    # 2. 测试 API
    echo -e "\n2. API 连通性测试"
    RESP=$(curl -s -w "\n%{http_code}" \
      "https://aime.tiktok-row.net/api/agents/v2/user/list/space?limit=1" \
      -H "authorization: Byte-Cloud-JWT ${JWT}" \
      -H "cookie: bd_sso_3b6da9=${JWT}")
    
    HTTP_CODE=$(echo "$RESP" | tail -n1)
    BODY=$(echo "$RESP" | sed '$d')
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo "✓ API 调用成功 (HTTP 200)"
    else
        echo "✗ API 调用失败 (HTTP $HTTP_CODE)"
        echo "  响应：$BODY"
    fi
    
    # 3. 检查工作空间
    echo -e "\n3. 工作空间检查"
    echo "$BODY" | jq -r '.spaces[0] | "  ID: \(.id)\n  名称：\(.name)"' 2>/dev/null || echo "  无法解析工作空间"
}

# 使用
debug_aime_api
```

## 最佳实践

### 1. Token 管理

- JWT token 有效期有限，建议在脚本中动态获取
- 不要硬编码 token 到脚本中
- token 过期时重新获取即可

### 2. 错误处理

```bash
#!/bin/bash
set -e  # 遇到错误立即退出

# 获取 JWT
JWT=$(NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest --site i18n-tt auth get-bytecloud-jwt-token) || {
    echo "获取 JWT 失败"
    exit 1
}

# 创建任务
RESPONSE=$(curl -s "https://aime.tiktok-row.net/api/agents/v2/sessions" \
  -X POST \
  -H "authorization: Byte-Cloud-JWT ${JWT}" \
  -H "cookie: bd_sso_3b6da9=${JWT}" \
  -d '{"role":3,"space_id":"c8cf4ea8-07c9-4082-8cad-ea98bf0ac626"}') || {
    echo "API 调用失败"
    exit 1
}

# 检查响应
ERROR=$(echo "$RESPONSE" | jq -r '.code // empty')
if [ "$ERROR" = "401" ]; then
    echo "认证失败，请重新获取 JWT"
    exit 1
fi
```

### 3. 参数验证

```bash
# 验证 space_id 格式
validate_space_id() {
    local id="$1"
    if [[ ! "$id" =~ ^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$ ]]; then
        echo "错误：无效的 space_id 格式"
        return 1
    fi
}

# 使用
validate_space_id "c8cf4ea8-07c9-4082-8cad-ea98bf0ac626" || exit 1
```

### 4. 日志记录

```bash
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

log "开始创建任务..."
log "Session ID: $SESSION_ID"
log "任务创建完成"
```
