# Hive (DataLeap) 数据目录

搜索和探索 DataLeap 数据目录中的 Hive/Clickhouse/Doris 数据资产。

## 命令

```bash
# 搜索数据库
bytedcli hive search --query "my_database" --type HiveDB --region cn

# 搜索表
bytedcli hive search --query "user" --type HiveTable --region gcp

# 获取数据库详情
bytedcli hive detail my_database --region cn

# 获取表详情（含完整 schema）
bytedcli hive detail my_database my_table --region gcp

# 通过 GUID 获取详情
bytedcli hive get <guid> --region cn

# 查看数据血缘
bytedcli hive lineage <guid> --region cn --depth 3
```

## 支持的资产类型

| 类型 | 说明 |
|------|------|
| `HiveDB` | Hive 数据库 |
| `HiveTable` | Hive 表 |
| `ClickhouseDB` | Clickhouse 数据库 |
| `ClickhouseTable` | Clickhouse 表 |
| `DorisTable` | Doris 表 |
| `DataTopics` | 数据主题 |

## 支持的区域

| 区域 | 说明 |
|------|------|
| `cn` | 中国（默认） |
| `sg` | 新加坡 |
| `gcp` / `eu` | 欧洲合规区 |

## 说明

- 默认资产类型为 `HiveDB`
- `detail` 和 `get` 命令会显示完整的表 schema（列名、类型、注释）
- `lineage` 显示上下游数据依赖关系
