---
name: bytedance-goofy-deploy
description: "Operate Goofy Deploy via bytedcli: list projects, view deployments, deploy new versions, rollback to existing versions. Use when tasks mention Goofy Deploy, web app deployments, or frontend deployments."
---

# bytedcli Goofy Deploy

## When to use

- Web 应用部署
- 前端项目部署
- 查看部署历史
- 查看项目/团队信息
- 触发新版本部署或回滚

## 前置条件

- 使用通用调用方式：`references/invocation.md`

> 示例省略 invocation 前缀。

## Quick start

```bash
# 列出支持的站点
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest goofy-deploy list-sites

# 获取团队信息
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest goofy-deploy get-team --team-id 4317 --site cn

# 列出团队下的项目
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest goofy-deploy list-projects --team-id 4317 --site cn

# 获取项目详情
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest goofy-deploy get-project --app-id 131716 --site cn

# 列出项目的部署区域
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest goofy-deploy list-regions --app-id 131716 --site cn

# 列出项目的部署通道
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest goofy-deploy list-channels --app-id 131716 --site cn

# 列出部署历史
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest goofy-deploy list-deployments --app-id 131716 --site cn

# 获取部署详情
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest goofy-deploy get-deployment --deploy-id 24913395 --site cn

# 部署新版本（需要 branch + commit）
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest goofy-deploy deploy-new --channel-id 3520795 --git-branch main --commit-hash abc123def --site cn

# 部署已有版本（回滚）
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest goofy-deploy deploy-version --channel-id 3520795 --scm-version 1.0.0.47 --site cn
```

## Notes

- 需要结构化输出加 `--json`（全局选项，放在子命令之前，如 `NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest --json goofy-deploy list-sites`）
- 站点选择用 `--site`（`cn|boe`），默认 `cn`
- 别名：`gd` = `goofy-deploy`
- 部署流程：先获取 channel-id，再使用 deploy-new 或 deploy-version

## Deployment Workflow

1. 获取项目 ID（已知或通过 `list-projects` 查询）
2. 列出通道：`list-channels --app-id <app_id>`
3. 选择通道 ID
4. 部署：
   - 新版本：`deploy-new --channel-id <id> --git-branch <branch> --commit-hash <hash>`
   - 已有版本：`deploy-version --channel-id <id> --scm-version <version>`

## References

- `references/goofy-deploy.md`
