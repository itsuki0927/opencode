# Recommend Cluster Reference — 集群推荐接口参考

> 本文件定义了集群推荐接口的完整参数规范、执行流程与输出格式。
> Plan Skill 在 **RESOLVE** 阶段缺少 cluster-config 时调用。

**CLI 命令**: `bits_env_cli recommend-cluster`

---

## 核心概念：集群 vs 实例 vs 机房

> 概念定义、语义解析表与调用次数规则详见 `concepts_ref.md` 第 4 节。
> 核心原则：**机房（IDC）是实例层面概念，一个集群可含多机房实例；N 个集群 = N 次调用。**

---

## 命令

```bash
bits_env_cli recommend-cluster --psm <psm> [选项]
```

---

## Input Parameters

### 必填参数

| Parameter | Flag | Type | Description |
|:----------|:-----|:-----|:------------|
| psm | `--psm` | string | 目标服务 PSM（如 `inf.hae.boe`） |

### 常用参数

| Parameter | Flag | Type | Default | Description |
|:----------|:-----|:-----|:--------|:------------|
| env | `--env` | string | — | 目标环境名称 |
| standard_env | `--standard-env` | string | `online_cn` | 标准环境标识。**MUST 与 INIT 阶段确定的值一致** |
| env_type | `--env-type` | string | `ppe` | 环境类型。若 standard_env 以 `boe` 开头则默认为 `boe_feature` |
| flow_base | `--flow-base` | string | `prod` | 流量基线 |
| specify_dcs | `--specify-dcs` | string | — | **指定机房**（逗号分隔）。一次调用中指定多个 = 一个集群内多机房实例 |

### 高级参数

| Parameter | Flag | Type | Default | Description |
|:----------|:-----|:-----|:--------|:------------|
| host_type | `--host-type` | string | — | 宿主类型 |
| ipv6_compatible | `--ipv6-compatible` | string | — | IPv6 兼容性 |
| multi_idc | `--multi-idc` | bool | `false` | 多机房推荐（容灾场景） |
| same_cluster | `--same-cluster` | bool | `false` | 倾向同一集群 |
| scenario | `--scenario` | string | — | 部署场景 |
| specify_clusters | `--specify-clusters` | string | — | 指定集群列表（逗号分隔） |
| specify_zones | `--specify-zones` | string | — | 指定区域列表（逗号分隔） |
| use_serverless | `--use-serverless` | string | — | Serverless 配额 |
| use_socket_quota | `--use-socket-quota` | string | — | Socket 配额 |

---

## standard-env 映射规则

> 完整枚举值详见 `concepts_ref.md` 第 5 节。
> **MUST**: 与 INIT 阶段确定的值保持一致，`ppe_` 用 `online_*`，`boe_` 用 `boe*`。

---

## 执行流程

### Step 1: 意图识别 — 多集群 vs 多机房实例

> 在构造 recommend-cluster 命令之前，**必须先判定用户意图**。

**判定逻辑**：

```
用户提到不同机房
    │
    ▼
  用户说"多个集群"/"N个集群"？
    │          │
    是         否（说"多个机房/实例" 或 仅列举机房名）
    ▼          ▼
  多集群模式    单集群多机房模式
  (每个机房      (一次调用
   单独调用)      --specify-dcs X,Y)
```

| 模式 | recommend-cluster 调用 | deploy-create 次数 |
|------|----------------------|-------------------|
| **多集群** | N 次，每次 `--specify-dcs <单个IDC>` | 每个集群 1 次 |
| **单集群多机房** | 1 次，`--specify-dcs IDC1,IDC2` | 按返回数组项数 |

### Step 2: 提取与推断参数

1. 提取 `psm`（必填），缺失则**询问用户**
2. 使用 INIT 阶段已确定的 `standard_env`，**不重新推断**
3. 根据 Step 1 判定结果构造 `--specify-dcs` 参数
4. 仅使用有值的参数构造命令

### Step 3: 预检 — 环境约束与冲突检测（条件触发）

> 用户指定了 `env` 且该环境已存在时执行，无 env 则跳过。

**3a. 环境元数据查询（机房约束）**:

```bash
bits_env_cli env-meta --env <env> [--standard-env <standard_env>]
```

- 若环境为单机房隔离 → 提取 IDC 值，在 Step 4 追加 `--specify-dcs <idc>`
- 若多机房或无限制 → 不添加

**3b. 已有部署查询（冲突检测）**:

```bash
bits_env_cli instance-meta --env <env> --psm <psm> [--standard-env <standard_env>]
```

- 若返回实例 → 对每个实例调用 `bits_env_cli instance-detail --id <id>`
- **记录已有集群的 Cluster Name 列表**，用于集群名冲突检测

### Step 4: 执行推荐命令

**场景 A — 单集群多机房实例**:
```bash
# "部署一个集群，实例在 HL 和 LQ"
bits_env_cli recommend-cluster --psm ecom.fulfillment.promise --standard-env online_cn --specify-dcs HL,LQ
```

**场景 B — 多集群各自单机房**:
```bash
# "部署两个集群，一个在 LF，一个在 LQ"
bits_env_cli recommend-cluster --psm bits.env.api --standard-env online_cn --specify-dcs LF
bits_env_cli recommend-cluster --psm bits.env.api --standard-env online_cn --specify-dcs LQ
```

**无指定机房**:
```bash
bits_env_cli recommend-cluster --psm inf.hae.boe --standard-env online_cn
```

---

## Output Format

### 返回结构

接口返回 **JSON 数组**，每个元素代表一个**集群**，其 `instanceList` 描述该集群下的实例在各机房的分布：

```json
[
  {
    "zone": "China-North-LF",
    "physicalCluster": "PPE",
    "logicalCluster": "default",
    "instanceList": [
      { "idc": "HL", "instanceCount": 1 },
      { "idc": "LQ", "instanceCount": 1 }
    ],
    "base_cluster_id": 558427
  }
]
```

### 字段说明

| 字段 | 类型 | 说明 |
|:-----|:-----|:-----|
| zone | string | 可用区。**精确值，禁止修改** |
| physicalCluster | string | 物理集群。**精确值，禁止修改** |
| logicalCluster | string | 逻辑集群。**精确值，禁止修改** |
| instanceList | array | **实例分布**：每项 = 一个机房中的实例，含 `idc` 和 `instanceCount` |
| base_cluster_id | number \| null | 对应 prod 线上集群 ID。有值时 deploy-create 需追加 `--base-cluster-id` |

### 理解返回值

```
返回数组的每个元素 = 一个集群（一次 deploy-create）
    └─ instanceList 的每个元素 = 该集群在某个机房中的实例
        └─ instanceCount = 该机房中的实例数量
```

> **一个集群 ≠ 一个机房**。一个集群可以包含分布在多个机房的实例。

---

## 返回值 → deploy-create 参数转换

### cluster-config 拼接规则

格式：`Zone|Physical|Logical|IDC1:count[,IDC2:count]`

**分隔符**: `|`（竖线）。机房部分：`IDC:count`，多个用 `,` 分隔。

#### 转换示例

**单机房实例**（instanceList 1 项）:

```json
{ "zone": "China-North-LF", "physicalCluster": "PPE", "logicalCluster": "default",
  "instanceList": [{"idc": "HL", "instanceCount": 1}] }
```
→ `--cluster-config "China-North-LF|PPE|default|HL:1"`

**多机房实例**（instanceList 多项，但仍是**同一个集群**）:

```json
{ "zone": "China-North-LF", "physicalCluster": "PPE", "logicalCluster": "ipv6",
  "instanceList": [{"idc": "HL", "instanceCount": 1}, {"idc": "LQ", "instanceCount": 1}] }
```
→ `--cluster-config "China-North-LF|PPE|ipv6|HL:1,LQ:1"`

### base-cluster-id 参数

| 条件 | deploy-create 参数 |
|------|-------------------|
| `base_cluster_id` 有值（非 null/0） | 追加 `--base-cluster-id <value>` |
| `base_cluster_id` 为 null 或 0 | 不追加 |

### 完整 deploy-create 命令示例

**单机房实例**:
```bash
bits_env_cli deploy-create \
  --env ppe_test --psm bits.env.api \
  --version 1.0.1.810 \
  --cluster-config "China-North-LF|PPE|default|HL:1" \
  --standard-env online_cn
```

**多机房实例（一个集群跨 HL+LQ）**:
```bash
bits_env_cli deploy-create \
  --env ppe_test --psm ecom.fulfillment.promise \
  --version 1.0.1.810 \
  --cluster-config "China-North-LF|PPE|ipv6|HL:1,LQ:1" \
  --base-cluster-id 558427 \
  --standard-env online_cn
```

**多集群（返回数组有多项 → 多次 deploy-create）**:
```bash
# 集群 1: logicalCluster=amd, 实例在 LQ
bits_env_cli deploy-create \
  --env ppe_test --psm bits.env.api \
  --version 1.0.1.810 \
  --cluster-config "China-North-LF|PPE|amd|LQ:1" \
  --base-cluster-id 5502161 \
  --standard-env online_cn

# 集群 2: logicalCluster=default, 实例在 HL
bits_env_cli deploy-create \
  --env ppe_test --psm bits.env.api \
  --version 1.0.1.810 \
  --cluster-config "China-North-LF|PPE|default|HL:1" \
  --base-cluster-id 5502161 \
  --standard-env online_cn
```

---

## ⚠️ Cluster Name 处理规则

> 集群名称默认为 `default`，**禁止随意修改**。

### 默认命名

- 返回值中不包含 clusterName 字段时，默认使用 `default`
- 多个集群时按返回顺序：`default` → `default2` → `default3`...（**无下划线**）

### 冲突判定

将集群名与 Step 3b 获取的**同一 PSM 下已有集群名**对比：

- 不冲突 → 直接使用
- 冲突 → 递增：`default` → `default2` → `default3`...

### 禁止行为

| ❌ 禁止 | ✅ 正确 |
|:--------|:--------|
| 改为 `default_lf`、`default_hl` 等带位置后缀 | 保持 `default` |
| 改为 `primary`、`main`、`cluster1` | 保持 `default` |
| 冲突时用 `default_2`（带下划线） | 用 `default2`（无下划线） |
| 用机房名当集群名（`hl_cluster`） | 机房是实例属性，不是集群属性 |

---

## Plan 使用要点

- **cluster-config 格式**: `Zone|Physical|Logical|IDC1:count[,IDC2:count]`
- **精确字符串**: zone、physicalCluster、logicalCluster、idc 均为精确值，**禁止修改**
- **instanceList → IDC 拼接**: 将 instanceList 中所有项拼为 `IDC1:count,IDC2:count`
- **base_cluster_id**: 有值时追加 `--base-cluster-id`，无值时不加
- **返回数组项数 = deploy-create 次数**: 每项对应一个集群，不是一个机房
- **standard-env 一致性**: 推荐时的 `--standard-env` 值必须与 deploy 中一致
- **多集群 vs 多机房**: 用户要 N 个集群 → N 次调用；用户要 1 个集群多机房 → 1 次调用带 `--specify-dcs`
