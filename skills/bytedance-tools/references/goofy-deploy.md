# Goofy Deploy

## 站点

```bash
# 列出支持的站点
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest goofy-deploy list-sites
```

## 团队与项目

```bash
# 获取团队详情
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest goofy-deploy get-team --team-id <team_id> --site cn

# 列出团队项目
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest goofy-deploy list-projects --team-id <team_id> --site cn --page 1 --page-size 20

# 获取项目详情
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest goofy-deploy get-project --app-id <app_id> --site cn
```

## 区域与渠道

```bash
# 列出部署区域
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest goofy-deploy list-regions --app-id <app_id> --site cn

# 列出部署渠道
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest goofy-deploy list-channels --app-id <app_id> --site cn
```

## 部署

```bash
# 列出部署历史
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest goofy-deploy list-deployments --app-id <app_id> --site cn --page 1 --page-size 20

# 获取部署详情
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest goofy-deploy get-deployment --deploy-id <deploy_id> --site cn

# 部署新版本（branch + commit）
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest goofy-deploy deploy-new \
  --channel-id <channel_id> \
  --git-branch <branch> \
  --commit-hash <hash> \
  --site cn

# 部署已有版本（回滚）
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest goofy-deploy deploy-version \
  --channel-id <channel_id> \
  --scm-version <version> \
  --site cn
```

## Notes

- 站点：`cn`（生产）、`boe`（测试）
- 别名：`gd` = `goofy-deploy`
- 部署流程：先获取 channel-id（`list-channels`），再使用 `deploy-new` 或 `deploy-version`
