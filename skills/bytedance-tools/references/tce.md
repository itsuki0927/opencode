# TCE

## 站点

```bash
# 列出支持的站点
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest tce list-sites
```

## 服务查询

```bash
# 收藏的服务
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest tce list-starred-service --page 1 --size 10

# 搜索服务
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest tce search-service --keyword "keyword" --env "ppe_xxx" --page 1 --size 10

# 获取服务详情
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest tce get-service <service_id> --tce-site prod

# 列出服务集群
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest tce list-service-clusters <service_id> --tce-site prod --page 1 --size 10
```

## 服务实例

```bash
# 推荐方式：使用 --psm + --env
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest tce list-service-instance --psm example.service.api --env prod --tce-site prod

# 兼容方式：使用 --service-id
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest tce list-service-instance --service-id <service_id> --tce-site prod --page 1 --size 10
```

## 环境级联查询

```bash
# 查询 PSM 的环境级联信息
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest tce env-cascader --psm example.service.api

# 指定分区
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest tce env-cascader --psm example.service.api --partition CN
```

## 泳道部署

```bash
# 部署泳道
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest tce deploy-lane \
  --env ppe_demo \
  --standard-env online_cn \
  --psm example.service.api \
  --flow-base prod \
  --branch master

# 部署指定 SCM 版本（仅提交指定仓库，不携带完整 SCM 列表）
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest tce deploy-lane \
  --env prod \
  --standard-env boe \
  --psm example.service.api \
  --flow-base boe \
  --scm-repo-name example/service/api \
  --scm-repo-version 1.0.0.8 \
  --action upgrade
```

## 跨站点示例

```bash
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest tce search-service --tce-site boe --keyword "my-service"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest tce search-service --tce-site byteintl --keyword "my-service"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest tce search-service --tce-site ttp-us-limited --keyword "my-service"
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest tce search-service --tce-site ttp-eu --keyword "my-service"
```

## Notes

- 站点别名：`cn=prod`、`i18n=byteintl`、`tx-ttp=ttp-us-limited`、`eu-ttp=ttp-eu`
- `list-service-instance` 推荐使用 `--psm + --env`，原位置参数改为 `--service-id` 选项
