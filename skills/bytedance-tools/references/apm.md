# APM

```bash
# 服务预览
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest apm service-preview --psm "psm.name" --service-type redis

# QPS
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest apm redis-qps --psm "toutiao.redis.coze_coding"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest apm redis-traffic --psm "toutiao.redis.coze_coding"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest apm service-qps --psm "example.service.api"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest apm service-qps --psm "example.service.api" --metric "service.request.server.throughput.total"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest apm downstream-qps --psm "example.service.api"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest apm downstream-qps --psm "example.service.api" --metric "service.request.downstream.throughput.total"

# Redis 监控
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest apm redis-overview --psm "toutiao.redis.coze_coding"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest apm redis-client --psm "toutiao.redis.coze_coding"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest apm redis-server --psm "toutiao.redis.coze_coding"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest apm redis-proxy --psm "toutiao.redis.coze_coding"

# 运行时 / 中间件
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest apm service-preview --psm "psm.name" --service-type runtime
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest apm service-preview --psm "psm.name" --service-type tlb
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest apm service-preview --psm "psm.name" --service-type tcc
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest apm service-preview --psm "psm.name" --service-type mysql
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest apm service-preview --psm "psm.name" --service-type agw_sidecar
```
