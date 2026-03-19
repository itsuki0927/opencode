# Settings

```bash
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli settings whitelist add --item-id "123" --title "demo" --whitelist "u1"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli settings whitelist save --whitelist-id 123 --code-file "./whitelist.save.py" --title "demo"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli settings whitelist delete --whitelist-id 123
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli settings whitelist list --item-id "123" --page-size 10 --page-no 0 --status 0 --type 0 --keyword ""
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli settings whitelist detail --whitelist-id 123
```
