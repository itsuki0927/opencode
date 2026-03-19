# bytedcli 通用调用方式

## 执行

```bash
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest --help
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest <command> [options]
```

## 站点切换

通过全局参数 `--site` 或环境变量 `BYTEDCLI_CLOUD_SITE` 切换 ByteCloud 站点：

| 站点值 | 说明 | SSO | 备注 |
|--------|------|-----|------|
| `prod` | 国内生产（默认） | `sso.bytedance.com` | |
| `i18n-tt` | TikTok 国际站 | `sso.tiktok-intl.com` | 需单独登录 |
| `i18n-bd` | ByteIntl 国际站 | `sso.bytedance.com` | 通常复用 prod 登录态 |
| `boe` | BOE 测试 | `test-sso.bytedance.net` | |
| `boei18n` | BOE 国际测试 | `sso.bytedance.com` | 通常复用 prod 登录态 |

> `--site i18n` 会归一化为 `i18n-bd`。

**重要：认证隔离按 SSO 环境生效。`i18n-tt`（TikTok SSO）需单独 `auth login`；`prod`、`i18n-bd`、`boei18n`（ByteDance SSO）通常共享登录态。** 切换站点前先检查认证状态：

```bash
# 检查 i18n-tt 站点认证
BYTEDCLI_CLOUD_SITE=i18n-tt NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest auth status

# 登录 i18n-tt 站点（使用 TikTok SSO）
BYTEDCLI_CLOUD_SITE=i18n-tt NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest auth login
```

站点切换示例：

```bash
# BOE
BYTEDCLI_CLOUD_SITE=boe NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest <command> [options]
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest --site boe <command> [options]

# i18n-tt（TikTok 国际站）
BYTEDCLI_CLOUD_SITE=i18n-tt NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest <command> [options]
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest --site i18n-tt <command> [options]

# i18n-bd（ByteIntl 国际站）
BYTEDCLI_CLOUD_SITE=i18n-bd NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest <command> [options]
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest --site i18n-bd <command> [options]

# BOEi18n
BYTEDCLI_CLOUD_SITE=boei18n NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest <command> [options]
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest --site boei18n <command> [options]
```

## JSON 输出

```bash
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest --json <command> [options]
```

注意：`--json` 是全局参数，必须放在 `<command>` 前面，例如 `--json auth status`，不能写成 `auth status --json`。

输出结构：

```json
{
  "status": "success|error",
  "data": {"...": "..."},
  "error": "error message",
  "context": {
    "execution_time_ms": 100,
    "timestamp": "2026-01-20T14:15:57.472335"
  }
}
```
