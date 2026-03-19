# RDS

## 数据库查询

```bash
# 列出收藏的数据库
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest rds list-starred-db --region cn --page 1 --size 50

# 搜索数据库
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest rds search-db "keyword" --region cn --page 0 --size 50

# 列出表
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest rds list-db-table "dbname" --region cn

# 执行 SQL
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest rds query-db "dbname" "SQL" --region cn
```

## 数据库详情

```bash
# 获取数据库基本信息
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest rds get-db "dbname" --region cn

# 数据库概览（详情 + 拓扑，可选 QPS）
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest rds get-db-overview "dbname" --region cn --qps

# 获取拓扑信息
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest rds get-db-topology "dbname" --region cn

# 获取 QPS
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest rds get-db-qps "dbname" --region cn

# 获取 SLA
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest rds get-db-sla "dbname" --region cn

# 获取表结构
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest rds get-db-table-schema "dbname" "table" --region cn

# 获取参数配置
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest rds get-db-params "dbname" --region cn
```

## 慢查询与诊断

```bash
# 获取慢查询配置
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest rds get-db-slow-config "dbname" --region cn

# 列出慢查询 SQL
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest rds list-db-slow-sql "dbname" --region cn --instance <ip> --port 3306

# 列出诊断项
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest rds list-db-diag "dbname" --region cn --page 0 --size 20

# 列出告警
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest rds list-db-alarm "dbname" --region cn

# 列出监控告警
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest rds list-db-alert "dbname" --region cn

# 获取运维详情
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest rds get-db-op-detail "dbname" --region cn
```

## BPM 工单管理（仅 boe/boei18n）

```bash
# 创建 DDL 工单 - ALTER（workflow-config-id: 812=DDL, 810=DML）
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest --site boe rds bpm-create \
  --workflow-config-id 812 \
  --ticket-type alter \
  --dbname "my_database" \
  --sql "ALTER TABLE users ADD COLUMN age INT;" \
  --background "变更原因"

# 创建 DDL 工单 - CREATE
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest --site boe rds bpm-create \
  --workflow-config-id 812 \
  --ticket-type create \
  --dbname "my_database" \
  --sql "CREATE TABLE new_table (id INT PRIMARY KEY);" \
  --background "创建新表"

# 创建 DML 工单（不需要 ticket-type）
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest --site boe rds bpm-create \
  --workflow-config-id 810 \
  --dbname "my_database" \
  --sql "UPDATE users SET status = 1 WHERE id = 100;" \
  --background "数据修复"

# 查看工单详情
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest --site boe rds bpm-get <record_id>

# 列出工单
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest --site boe rds bpm-list --dbname "my_database"

# 取消工单
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest --site boe rds bpm-cancel <record_id> --reason "取消原因"

# 更新工单 SQL
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest --site boe rds bpm-update-sql <record_id> --sql "新的 SQL"
```

## Notes

- BPM 工单仅在 `boe`/`boei18n` 站点可用，需要 `--site boe` 或 `--site boei18n`
- BPM 审批/拒绝请使用 BPM Web UI
- workflow-config-id: 812=DDL（表结构变更），810=DML（数据变更）
- DDL 工单需要 `--ticket-type`：`alter`（修改表）或 `create`（创建表），DML 工单不需要
