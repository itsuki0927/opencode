# BAM

```bash
# PSM 列表
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest bam list-recent-psm --cluster default
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest bam list-starred-psm --cluster default
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest bam search-psm "codebase.app.openapi" --cluster default

# 方法列表 / 详情
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest bam list-method --psm "codebase.app.openapi"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest bam get-method --endpoint-id 2404309 --version 1.0.337
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest bam get-method --psm "codebase.app.openapi" --method "GetRepository"

# 版本历史
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest bam versions "codebase.app.openapi" --cluster default
```
