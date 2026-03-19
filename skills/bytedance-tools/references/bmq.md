# BMQ

```bash
# Topic 列表
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest bmq topics --vregion "US-BOE" --page 1 --size 20
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest bmq topics --vregion "Singapore-Central" --search "pipo" --all

# Topic 详情
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest bmq topic 12345 --vregion "US-BOE"

# Cluster 列表
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest bmq clusters --vregion "US-BOE" --all
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest bmq clusters --vregion "Singapore-Central" --search "public"

# Consumer Group 列表
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest bmq consumers --vregion "US-BOE" --page 1 --size 20
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest bmq consumers --vregion "Singapore-Central" --search "data_inventory" --all

# Mirror 列表
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest bmq mirrors --vregion "Singapore-Central" --status RUNNING --all
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest bmq mirrors --vregion "Singapore-Central" --search "topic_name" --size 10

# 多站点（TikTok ROW）
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest --site i18n-tt bmq topics --vregion "Singapore-Central" --all
```
