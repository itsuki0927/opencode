# ENV

```bash
# 站点与动态 standard_env 列表
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest env list-sites

# 收藏/管理 ENV
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest env list-starred-env --page 1 --size 10
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest env list-managed-env --page 1 --size 10

# 按环境标识搜索
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest env search-env --keyword "ppe_coze" --env-site cn,boe

# 按服务搜索
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest env search-service --service "example.service.api" --env-site cn,boe

# 部署与升级
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest env deploy-tce-service --env "ppe_demo" --standard-env online_i18nbd --psm "flow.bot.open_gateway" --flow-base prod
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest env deploy-tcc-service --env "ppe_demo" --standard-env online_i18nbd --psm "ocean.cloud.bot_adapter"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest env upgrade-tce-service --env "ppe_demo" --standard-env online_i18nbd --psm "flow.bot.open_gateway" --cluster-id 350079955 --branch "feat/demo"

# 设备管理
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest env list-device --env "ppe_demo" --standard-env online_i18nbd
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest env add-device --env "ppe_demo" --standard-env online_i18nbd --device-id 4252524525 --expire-at "2026-02-19T01:19:40.471Z"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest env update-device-expire --env "ppe_demo" --standard-env online_i18nbd --device-id 4252524525 --expire-at "2026-02-19T09:19:58+08:00"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest env unbind-device --standard-env online_i18nbd --device-id 4252524525

# 工单
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest env list-ticket --env "ppe_demo" --standard-env online_i18nbd --page 1 --size 10
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest env get-ticket --ticket-id 2021755505366867968 --standard-env online_i18nbd
```
