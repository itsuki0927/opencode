# Cache

```bash
# 服务列表
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest cache list-starred-service --page 1 --size 20
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest cache search-service --keyword "cache.demo" --page 1 --size 20
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest cache get-service --psm "cache.demo"

# Redis 命令
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest cache execute-command --psm "cache.demo" --command "GET" --args "key"

# 慢查询 / 大热 Key
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest cache slow-log --psm "cache.demo"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest cache list-big-keys --psm "cache.demo" --date "2026-02-05" --begin "00:00:00" --end "23:59:59"

# 工单
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest cache list-my-tickets --psm "cache.demo"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest cache list-service-tickets --psm "cache.demo" --page 1 --size 20
```
