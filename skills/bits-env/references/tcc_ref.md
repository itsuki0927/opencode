# TCC Deploy Reference — TCC 类型服务部署接口参考

> 本文件定义了 **TCC 类型服务**的部署命令参数与输出格式。
> Plan Skill 在 **EXECUTE** 阶段对 `service-type=tcc` 的服务调用。
>
> **重要边界**：环境平台（bits_env_cli）仅负责 TCC 服务的**创建部署**（tcc-deploy-create）。
> 服务创建完成后，TCC 服务内部的配置创建/发布/查询等操作使用 **TCC 平台自身的命令**执行，
> **不属于**环境编排流程（FSM），不在本文件和 SKILL.MD 的管辖范围内。

**CLI 命令**: `bits_env_cli`

---

## 命令总览

| # | 命令 | 用途 | 适用场景 |
|:--|:-----|:-----|:---------|
| 1 | `tcc-deploy-create` | 在环境中创建 TCC 类型服务 | CREATE_NEW / DEPLOY_TO_ENV / CLONE / BATCH_DEPLOY（service-type=tcc） |

> **核心规则**: `tcc-deploy-create` **不需要** `--namespace` 参数，仅需 `--env` 和 `--psm`。
> 后续 TCC 平台操作命令（tcc-create-config 等）中的 `--namespace` 与 `psm` 是同一概念，自动令 `--namespace = psm`，无需额外询问用户。

> **注意**: TCC 服务无 `tcc-deploy-upgrade` 命令。TCC 服务的配置更新通过 TCC 平台命令完成，不走环境部署流程。
>
> **交叉引用**: TCE 类型服务的部署命令请参考 `deploy_ref.md`。

---

## 1. TCC Deploy Create — 创建 TCC 服务

### 适用场景

- 在环境中创建新的 TCC 类型服务
- 服务账号批量部署 TCC 服务（BATCH_DEPLOY）

### Command

```bash
bits_env_cli tcc-deploy-create \
  --env <env> \
  --psm <psm> \
  [--service-id <id>] \
  [--region <region>] \
  [--standard-env <standard_env>] \
  [--env-type <env_type>] \
  [--service-auth]
```

### Input Parameters

| Parameter | Flag | Required | Default | Description |
|:----------|:-----|:---------|:--------|:------------|
| env | `--env` | **YES** | — | 目标环境名称。不存在时自动创建。格式: `ppe_[a-z0-9_]+` 或 `boe_[a-z0-9_]+` |
| psm | `--psm` | **YES** | — | 服务 PSM。格式: 点分隔标识符 |
| service_id | `--service-id` | NO | 自动解析 | TCC service_id，不传则通过 psm 搜索接口解析 |
| region | `--region` | NO | 自动推断 | region，不传则通过 conf_space 解析并优先选择 `CN` |
| standard_env | `--standard-env` | NO | 自动推断 | `online_cn`（ppe）/ `boe`（boe） |
| env_type | `--env-type` | NO | 自动推断 | 环境类型。`ppe_` 前缀 → `ppe`，`boe_` 前缀 → `boe_feature` |
| service_auth | `--service-auth` | NO | `false` | 服务账号模式开关。BATCH_DEPLOY 场景必须携带 |

### TCC vs TCE 参数差异

| 参数 | TCE (deploy-create) | TCC (tcc-deploy-create) |
|------|--------------------|-----------------------|
| `--env` | ✅ | ✅ |
| `--psm` | ✅ | ✅ |
| `--standard-env` | ✅ | ✅ |
| `--namespace` | ❌ | ❌ 不需要（TCC 平台操作命令使用，=PSM） |
| `--cluster-config` | ✅ | ❌ 不适用 |
| `--cluster-name` | ✅ | ❌ 不适用 |
| `--version` / `--branch` | ✅ | ❌ 不适用 |
| `--base-cluster-id` | ✅ | ❌ 不适用 |
| `--cpu-mem` | ✅ | ❌ 不适用 |
| `--single-idc` | ✅ | ❌ 不适用 |
| `--service-auth` | ✅ | ✅ |

> **关键差异**: TCC 服务**不需要** cluster-config、version/branch、cpu-mem 等参数。
> TCC 服务的部署（tcc-deploy-create）只需要确定"在哪个环境中、为哪个 PSM 创建"。

### Output Format

```text
### TCC Deployment Initiated
| Item | Value | Description |
| :--- | :--- | :--- |
| Env Name | {env_name} | 目标环境名称 |
| Service | {psm} | 服务 PSM |
| Service Type | TCC | 服务类型 |
| Namespace | {namespace} | TCC 命名空间 |
| Action | Create | 操作类型 |
| Status | Success | 提交状态 |
| Ticket ID | {ticket_id} | 关联工单 ID |
```

### 完整命令示例

**基础创建**:
```bash
bits_env_cli tcc-deploy-create \
  --env ppe_test --psm config.center.service \
  --standard-env online_cn
```

**服务账号批量部署**:
```bash
bits_env_cli tcc-deploy-create \
  --env ppe_batch --psm config.center.service \
  --standard-env online_cn \
  --service-auth
```

**混合部署场景（与 TCE 服务一起批量部署）**:
TCC 与 TCE 服务可同时出现在一次 BATCH_DEPLOY 中。两类服务使用各自的部署命令，互不影响：
- TCE 服务 → `deploy-create` / `deploy-upgrade`
- TCC 服务 → `tcc-deploy-create`

---

## Validation Checklist — TCC EXECUTE 前必检清单

| # | 检查项 | 违反动作 |
|:--|:-------|:---------|
| 1 | `env` 格式合法 (`ppe_[a-z0-9_]+` 或 `boe_[a-z0-9_]+`) | ABORT |
| 2 | `psm` 格式合法（含 `.` 分隔） | ABORT |
| 3 | `tcc-deploy-create` 不携带 `--namespace`（该参数仅用于 TCC 平台操作命令） | **REJECT**: 移除参数 |
| 4 | `standard-env` 已填写且为合法枚举值 | 补充默认值 |
| 5 | BATCH_DEPLOY 时携带 `--service-auth` | REJECT, 补充 flag |
| 6 | **禁止**携带 TCE 专有参数（`--cluster-config`、`--version`、`--branch` 等） | REJECT, 移除 |

---

## FSM 阶段说明（TCC 特殊处理）

> 以下说明 TCC 服务在 FSM 各阶段的特殊行为，与 SKILL.MD 主文件配合使用。

| FSM 阶段 | TCC 行为 |
|----------|---------|
| **INIT** | 识别 `service-type=tcc`。不提取 version/branch/cluster-config/cpu-mem/namespace |
| **SEARCH** | 通过 `instance-meta` 检查服务是否已存在。已存在则告知用户（无 upgrade 操作） |
| **VALIDATE** | 执行 SV-12（禁止 TCE 专有参数和 --namespace）、SV-13（仅需 env+psm+standard-env）、SV-14（service-type 合法） |
| **RESOLVE** | **跳过**。不需要 recommend-cluster 和版本推荐流程 |
| **PLAN** | 纳入部署计划，标注 `Type: TCC`。混合部署时与 TCE 服务一起展示 |
| **EXECUTE** | 调用 `tcc-deploy-create`。可与 TCE 服务并行执行。无先锋-跟随 |
| **MONITOR** | TCC 工单纳入正常监控流程，终态判断与 TCE 相同 |

---

## TCC 平台操作命令参考

> **Skill 使用范围说明**:
> - FSM EXECUTE 阶段**仅调用** `tcc-deploy-create`（在环境中创建 TCC 服务）。
> - 以下 `tcc-*` 命令已集成到 `bits_env_cli` 中，LLM 可直接调用，但**不纳入 SKILL.MD 的 FSM 流程**。
> - 当用户在部署完 TCC 服务后询问配置操作时，LLM 应引导用户使用以下命令。

### 命令总览

| # | 命令 | 用途 | 适用场景 |
|:--|:-----|:-----|:---------|
| 1 | `tcc-list-sites` | 列出可用 TCC 站点 | 选站点、排障 |
| 2 | `tcc-search-namespace` | 搜索命名空间（namespace） | 找 namespace / 判断是否存在 |
| 3 | `tcc-list-dir` | 列出目录（dir）及其 ID | 解析 `dir-id`、排障 |
| 4 | `tcc-list-config` | 列出 namespace 下配置项 | 查询配置列表 |
| 5 | `tcc-get-config` | 查询单个配置详情 | 获取 config_id / 版本 / 内容 |
| 6 | `tcc-create-config` | 创建配置（支持 v2 namespace 自动回退） | 首次创建配置 |
| 7 | `tcc-update-config` | 更新配置（支持同步 region 组扩展） | 修改配置内容 |
| 8 | `tcc-deploy-config` | 发布配置（支持 manual/auto/force-auto） | 发布/滚动发布 |
| 9 | `tcc-publish-detail` | 查询发布单详情 | 观察发布进度 |
| 10 | `tcc-operate-deployment` | 操作发布单步骤（start/finish/review） | 手动推进/审批 |
| 11 | `tcc-approve-deployment` | 审批通过发布单 review 步骤 | review 通过 |
| 12 | `tcc-reject-deployment` | 审批驳回发布单 review 步骤 | review 驳回 |

---

### 公共参数说明

#### env / region / dir

| 参数 | Flag | Required | Default | Description |
|:--|:--|:--:|:--|:--|
| env | `--env` | ⚠️ 按命令 | 命令不同 | TCC 环境，例如 `prod` / `ppe` / `ppe_*` / `boe` / `boe_*` |
| standard_env | `--standard-env` | ⚠️ 按命令 | 命令不同 | 集群环境，例如 `boe` / `online_cn` 等 |
| region | `--region` | ⚠️ 按命令 | `CN` | 区域，例如 `CN`、`China-East` |
| dir | `--dir` | ⚠️ 按命令 | `/default` | 目录路径（目录 ID 由系统内部维护） |
| dir_id | `--dir-id` | NO | 自动解析 | 目录 ID。目录为空时必须依赖 `tcc-list-dir` 解析；若解析失败需手动提供 |

---

### 1. tcc-list-sites — 列出站点

```bash
bits_env_cli tcc-list-sites
```

**输出**: JSON 数组，每项包含 `key / origin / apiRoot / jwtHost / needTenantHeader`。

---

### 2. tcc-search-namespace — 搜索命名空间

```bash
bits_env_cli tcc-search-namespace \
  --keyword <keyword> \
  [--env <env>] \
  [--tcc-site <site>]
```

| Parameter | Flag | Required | Default | Description |
|:--|:--|:--:|:--|:--|
| keyword | `--keyword` | YES | — | 搜索关键字 |
| env | `--env` | NO | `prod` | web API 环境 |
| tcc_site | `--tcc-site` | NO | 自动推断 | 站点 |

---

### 3. tcc-list-dir — 列出目录（用于拿 dir-id）

```bash
bits_env_cli tcc-list-dir \
  --namespace <namespace> \
  [--env <env>] \
  [--tcc-site <site>] \
  [--region <region>] \
  [--no-return-empty]
```

| Parameter | Flag | Required | Default | Description |
|:--|:--|:--:|:--|:--|
| namespace | `--namespace` | YES | — | 命名空间（= PSM） |
| env | `--env` | NO | `prod` | web API 环境 |
| tcc_site | `--tcc-site` | NO | 自动推断 | 站点 |
| region | `--region` | NO | — | 可选区域过滤 |
| no_return_empty | `--no-return-empty` | NO | `false` | 不返回空目录 |

**输出字段（常用）**:
- `dirs[].id`：目录 ID（用于 `--dir-id`）
- `dirs[].path`：目录路径（例如 `/default`）
- `dirs[].description`：目录描述
- `dirs[].owners`：owner 列表

---

### 4. tcc-list-config — 列出配置列表

```bash
bits_env_cli tcc-list-config \
  --namespace <namespace> \
  [--region <region>] \
  [--env <env>] \
  [--tcc-site <site>]
```

> **注意**: BOE 站点读 `CN` 时可能映射为 `all_region`（兼容 TCC 读取规则）。

---

### 5. tcc-get-config — 查询配置详情

```bash
bits_env_cli tcc-get-config \
  --namespace <namespace> \
  --config-name <config_name> \
  [--region <region>] \
  [--dir <dir>] \
  [--env <env>] \
  [--tcc-site <site>]
```

---

### 6. tcc-create-config — 创建配置

```bash
bits_env_cli tcc-create-config \
  --namespace <namespace> \
  --config-name <config_name> \
  --description <desc> \
  [--env <env>] \
  [--tcc-site <site>] \
  [--region <region>] \
  [--dir <dir>] \
  [--dir-id <id>] \
  [--data-type <yaml|json|string>] \
  [--config-type <static|...>] \
  (--value <value> | --file <path>) \
  [--tags <a,b>] \
  [--note <note>]
```

| Parameter | Flag | Required | Default | Description |
|:--|:--|:--:|:--|:--|
| namespace | `--namespace` | YES | — | 命名空间（= PSM） |
| config_name | `--config-name` | YES | — | 配置名 |
| description | `--description` | YES | — | 配置描述（TCC Web 创建要求非空） |
| env | `--env` | NO | `ppe` | 目标环境 |
| tcc_site | `--tcc-site` | NO | 自动推断 | 站点 |
| region | `--region` | NO | `CN` | 区域 |
| dir | `--dir` | NO | `/default` | 目录路径 |
| dir_id | `--dir-id` | NO | 自动解析 | 目录 ID。若目录为空且自动解析失败，需要手动提供 |
| data_type | `--data-type` | NO | `yaml` | 数据类型 |
| config_type | `--config-type` | NO | `static` | 配置类型 |
| value | `--value` | 二选一 | — | 直接传值 |
| file | `--file` | 二选一 | — | 从文件读取值 |
| tags | `--tags` | NO | — | 逗号分隔标签 |
| note | `--note` | NO | — | 备注 |

---

### 7. tcc-update-config — 更新配置

```bash
bits_env_cli tcc-update-config \
  --namespace <namespace> \
  --config-name <config_name> \
  [--env <env>] \
  [--tcc-site <site>] \
  [--region <region>] \
  [--dir <dir>] \
  (--value <value> | --file <path>) \
  [--description <desc>] \
  [--data-type <yaml|json|string>] \
  [--config-type <static|...>] \
  [--tags <a,b>] \
  [--note <note>]
```

> **同步 region 组**: 若配置属于同步 region 组（例如 `CN` + `China-East`），更新时会自动扩展到该组内已存在副本。

---

### 8. tcc-deploy-config — 发布配置

```bash
bits_env_cli tcc-deploy-config \
  --namespace <namespace> \
  --config-name <config_name> \
  [--env <env>] \
  [--tcc-site <site>] \
  [--region <region>] \
  [--from-version <n>] \
  [--to-version <n>] \
  [--strategy-id <id>] \
  [--remark <remark>] \
  [--publish-mode <manual|auto|force-auto>]
```

**publish-mode 说明**:

| Mode | 行为 |
|:--|:--|
| `manual` | 仅创建发布单，不自动 start/finish（用于手动滚动） |
| `auto` | 默认：不需要 review 则自动 start/finish；需要 review 则返回 review 信息 |
| `force-auto` | 强制自动推进，忽略 review 要求（尽力推进） |

**输出（关键字段）**:
- `deployment_id`：发布单 ID
- `console_url`：控制台 publish-details 链接
- `need_review`：是否需要审批

---

### 9. tcc-publish-detail — 查询发布单详情

```bash
bits_env_cli tcc-publish-detail \
  --deployment-ref <id_or_publish_details_url> \
  [--env <env>] \
  [--tcc-site <site>]
```

**deployment-ref 支持**:
- 数字 ID：`2829686318612368`
- URL：`https://cloud.bytedance.net/tcc/namespace/<ns>/publish-details/<id>`

---

### 10. tcc-operate-deployment — 操作发布单

```bash
bits_env_cli tcc-operate-deployment \
  --deployment-ref <id_or_publish_details_url> \
  --operation <start|finish|review_pass|review_reject> \
  [--current-step-index <n>] \
  [--env <env>] \
  [--tcc-site <site>]
```

> 未传 `--current-step-index` 时，CLI 会尝试自动推断当前步骤；推断失败时需要手动指定。

---

### 11. tcc-approve-deployment — 通过审批

```bash
bits_env_cli tcc-approve-deployment \
  --deployment-ref <id_or_publish_details_url> \
  [--current-step-index <n>] \
  [--env <env>] \
  [--tcc-site <site>]
```

---

### 12. tcc-reject-deployment — 驳回审批

```bash
bits_env_cli tcc-reject-deployment \
  --deployment-ref <id_or_publish_details_url> \
  [--current-step-index <n>] \
  [--env <env>] \
  [--tcc-site <site>]
```

---

## 典型工作流示例

### 场景 A: 部署 TCC 服务后创建并发布配置

```
1. tcc-deploy-create  → 在环境中创建 TCC 服务（FSM EXECUTE 阶段）
2. tcc-create-config  → 为该 namespace 创建一个配置项
3. tcc-deploy-config  → 发布该配置（auto 模式）
4. tcc-publish-detail → 查看发布进度
5. (如需审批) tcc-approve-deployment → 通过 review 步骤
```

### 场景 B: 更新已有配置并发布

```
1. tcc-list-config    → 列出 namespace 下的配置项
2. tcc-get-config     → 查看当前配置内容和版本
3. tcc-update-config  → 更新配置内容
4. tcc-deploy-config  → 发布新版本
5. tcc-publish-detail → 监控发布进度
```

### 场景 C: 排查命名空间和目录

```
1. tcc-list-sites           → 确认站点
2. tcc-search-namespace     → 搜索目标 namespace
3. tcc-list-dir             → 获取目录列表和 dir-id
4. tcc-list-config          → 列出该目录下的配置
```