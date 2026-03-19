# 常见问题与处理

## 1. Missing command

- 原因：未指定子命令
- 处理：`NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest <group> --help`

## 2. Missing argument

- 原因：缺少必需位置参数
- 处理：使用 `--help` 查看参数

## 3. Not authenticated

- 原因：未登录或 Token 过期
- 处理：`NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest auth login`

## 4. 获取字节云 JWT 失败: 401

- 原因：目标站点未认证。认证隔离按 SSO 环境生效：`i18n-tt`（TikTok SSO）与 `prod/i18n-bd/boei18n`（ByteDance SSO）隔离。即使 prod 已登录，操作 i18n-tt 仍需单独认证
- 处理：为目标站点执行登录
  ```bash
  # 以 i18n-tt 为例
  BYTEDCLI_CLOUD_SITE=i18n-tt NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest auth login
  ```
- 验证：`BYTEDCLI_CLOUD_SITE=i18n-tt NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest auth status`

## 5. 网络/权限问题

- 确认内网访问权限
- 确认已登录且 Token 有效
