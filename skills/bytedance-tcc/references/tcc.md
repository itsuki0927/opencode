# TCC

```bash
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest tcc list-sites
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest tcc list-starred-namespace --tcc-site prod --page 1 --size 50
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest tcc search-namespace "keyword" --tcc-site prod --scope all --page 1 --size 50

NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest tcc list-config "namespace" --region CN
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest tcc get-config "namespace" "config_name" --region CN --dir "/default"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest tcc list-dir "namespace" --env ppe_xxx --tcc-site i18n-bd
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest tcc list-meta-data --env ppe_xxx --tcc-site i18n-bd

NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest tcc create-config "namespace" "config_name" --env ppe --tcc-site prod --region CN --dir "/default" --value "a: b"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest tcc update-config "namespace" "config_name" --env ppe --tcc-site prod --region CN --value "a: b"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest tcc import-base-config "namespace" --config-ids "123,456" --target-env ppe_xxx --tcc-site i18n-bd

# Deploy config (default: --publish-mode auto, auto start + finish when no review needed)
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest tcc deploy-config "namespace" "config_name" --env ppe --tcc-site prod --region CN

# Only create deployment, do not start (manual mode)
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest tcc deploy-config "namespace" "config_name" --env ppe --tcc-site prod --region CN --publish-mode manual

# Deploy with review support (auto mode): returns review info when review is needed
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest tcc deploy-config "namespace" "config_name" --env prod --tcc-site prod --region CN --publish-mode auto

# Force auto-publish regardless of review requirement
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest tcc deploy-config "namespace" "config_name" --env prod --tcc-site prod --region CN --publish-mode force-auto
```
