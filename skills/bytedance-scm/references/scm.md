# SCM

```bash
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest scm list-starred-repo --page 1 --size 10
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest scm search-repo "byteapi/command/bytedcli"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest scm list-repo-version "byteapi/command/bytedcli" --branch master --type online --status build_ok
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest scm build-repo "byteapi/command/bytedcli" --branch master --type test -e '{"CUSTOM_KEY":"VALUE"}' -m "trigger build reason"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest scm get-build-log "byteapi/command/bytedcli" "1.0.0.1686" --step building
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest scm get-build-log "byteapi/command/bytedcli" "1.0.0.1686" --status failed
```
