# Netlink

Netlink 提供域名接入与 TLB servername/location 配置能力。

常用命令（示例均使用内部源 npx）：

```bash
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest netlink list-sites
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest netlink search-domain --keyword "api.coze.cn"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest netlink list-domain-configs --domain "api.coze.cn"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest netlink search-path --domain "api.coze.cn" --keyword "submit_tool_outputs"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest netlink get-path-config --domain "api.coze.cn" --path "/v3/chat/submit_tool_outputs"
```

环境切换：

```bash
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest netlink search-domain --netlink-site boe --keyword "example.com"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest netlink search-domain --netlink-site i18n --keyword "docs.coze.com"
```

