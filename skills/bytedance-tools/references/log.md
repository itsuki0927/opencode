# Log

```bash
# PSM 日志搜索
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest log search-psm-log --psm "psm.name" --start "2026-02-02T08:00:00" --end "2026-02-02T09:00:00"

# PSM 日志搜索（默认写入临时文件，并在控制台打印文件路径）
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest log search-psm-log --psm "psm.name" --start "2026-02-02T08:00:00" --end "2026-02-02T09:00:00" --output file

# PSM 日志搜索（直接输出到控制台）
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest log search-psm-log --psm "psm.name" --start "2026-02-02T08:00:00" --end "2026-02-02T09:00:00" --output console

# PSM 日志搜索（指定输出文件）
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest log search-psm-log --psm "psm.name" --start "2026-02-02T08:00:00" --end "2026-02-02T09:00:00" --output file --output-file "/tmp/bytedcli.search.log"

# PSM 日志搜索（按 KV 过滤）
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest log search-psm-log --psm "example.service.api" --keyword "deploy" --kv-filter "method=Deploy|Rollback" --kv-filter "_idc=lf|hl"

# LogID 查询
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest log get-logid-log "20260202085428C91A145A63CB5F0B9D80" --psm "psm.name"

# LogID 查询（默认写入临时文件，并在控制台打印文件路径）
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest log get-logid-log "20260202085428C91A145A63CB5F0B9D80" --psm "psm.name" --output file

# LogID 查询（直接输出到控制台）
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest log get-logid-log "20260202085428C91A145A63CB5F0B9D80" --psm "psm.name" --output console

# LogID 查询（指定输出文件）
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest log get-logid-log "20260202085428C91A145A63CB5F0B9D80" --psm "psm.name" --output file --output-file "/tmp/bytedcli.logid.log"

# 泳道实例日志
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest log get-lane-instance-log "psm.name" --env "ppe_xxx" --start "2026-02-02T08:00:00"

# 生产实例日志
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest log search-prod-instance-log --psm "psm.name" --env prod --region "China-North" --range 1h --keyword "error"

# 生产实例日志（默认写入临时文件，并在控制台打印文件路径）
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest log search-prod-instance-log --psm "psm.name" --env prod --region "China-North" --range 1h --keyword "error" --output file

# 生产实例日志（直接输出到控制台）
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest log search-prod-instance-log --psm "psm.name" --env prod --region "China-North" --range 1h --keyword "error" --output console

# 生产实例日志（指定输出文件）
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest log search-prod-instance-log --psm "psm.name" --env prod --region "China-North" --range 1h --keyword "error" --output file --output-file "/tmp/bytedcli.prod.instance.log"

# 日志聚类
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest log get-log-cluster "psm.name" --start "2026-02-02T08:00:00"
```
