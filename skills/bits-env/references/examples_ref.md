# Examples Reference — 部署示例集

> 本文件包含 SKILL.MD 的全部部署示例，供 LLM 参考理解各场景的 FSM 执行流程。
> **本文件为只读参考**，不影响 FSM 执行逻辑。

---
## Examples

### Example 1: Clone Environment
**User**: "Clone ppe_source to ppe_target"

1. **[INIT]** Intent=CLONE, source=ppe_source, target=ppe_target.
2. **[SEARCH]** `instance-meta --env ppe_source` → 所有服务及 ID。并行 `instance-detail`。
3. **[VALIDATE]** 检查 target 环境；验证所有 cluster-config 精确值。
4. **[PLAN]** Phase 1=创建 target; Phase 2=先锋集群; Phase 3=跟随集群并行。
5. **[EXECUTE]** 先锋 → 等待服务创建 → 跟随并行。
6. **[MONITOR]** 轮询所有 Ticket 至终态。
7. **[COMPLETE]** 汇总报告。

### Example 2: Deploy Branch to New Environment (本地 Git)
**User**: "Deploy current branch to 'ppe_feat_x'"
**Context**: git 仓库 `my.service.psm`, 分支 `feat/new-api`.

1. **[INIT]** Intent=CREATE_NEW, env=ppe_feat_x, psm=my.service.psm, branch=feat/new-api.
   （用户在 Git 仓库中，匹配目标服务 → 情况 A，允许使用 --branch）
2. **[SEARCH]** 环境未找到。
3. **[RESOLVE]** `recommend-cluster` → `China-North-LF|PPE|default|LF:1`.
4. **[EXECUTE]** `bits_env_cli deploy-create --env ppe_feat_x --psm my.service.psm --branch feat/new-api --cluster-config "China-North-LF|PPE|default|LF:1" --standard-env online_cn`
5. **[MONITOR]** 轮询。
6. **[COMPLETE]** ✅

### Example 3: Deploy Service to Existing Environment (非本地 Git → --version)
**User**: "Deploy 'user.auth' to 'ppe_stable'"

1. **[INIT]** Intent=DEPLOY_TO_ENV, env=ppe_stable, psm=user.auth.
2. **[SEARCH]** 环境存在，user.auth 不在列表中。
3. **[RESOLVE]** recommend-cluster → `China-North-LF|PPE|default|LF:1`; recommend-version → version=1.0.1.810 (prod baseline).
4. **[EXECUTE]** `bits_env_cli deploy-create --env ppe_stable --psm user.auth --version 1.0.1.810 --cluster-config "China-North-LF|PPE|default|LF:1" --standard-env online_cn`
5. **[MONITOR]** 轮询。
6. **[COMPLETE]** ✅

### Example 4: Multi-Service Multi-Cluster (先锋-跟随)
**User**: "在 ppe_test 部署 bits.env.api 和 inf.hae.boe，每个服务各 2 个集群"

1. **[INIT]** Intent=CREATE_NEW, env=ppe_test, psm=[bits.env.api, inf.hae.boe], clusters_per_service=2.
2. **[SEARCH]** 两个服务均不存在。
3. **[RESOLVE]** 并行为两个服务各调用 recommend-cluster (2 个集群) + recommend-version → 各服务获取 prod baseline version。
4. **[PLAN]** Phase 1=创建环境; Phase 2=先锋; Phase 3=跟随。
5. **[EXECUTE]** 先锋并行 → 等待各服务"创建服务 (Succeed)" → 跟随并行。
6. **[MONITOR]** 轮询全部 4 个 Ticket。
7. **[COMPLETE]** 前置条件验证 (4/4) → 汇总报告。

### Example 5: Upgrade Existing Service
**User**: "Update 'user.auth' in 'ppe_stable' to version 1.0.2"

1. **[INIT]** Intent=UPGRADE, env=ppe_stable, psm=user.auth, version=1.0.2.
2. **[SEARCH]** `instance-meta` → 集群 `default` (ID: 123).
3. **[EXECUTE]** `bits_env_cli deploy-upgrade --env ppe_stable --psm user.auth --version 1.0.2 --cluster-id 123 --standard-env online_cn`
4. **[MONITOR]** 轮询。
5. **[COMPLETE]** ✅

### Example 6: Multi-Service Upgrade (全量并行)
**User**: "升级 ppe_stable 中的 service.a 和 service.b 到最新版本"

1. **[INIT]** Intent=UPGRADE, env=ppe_stable, psm=[service.a, service.b].
2. **[SEARCH]** 两个服务各有 3 个集群。
3. **[RESOLVE]** 并行 recommend-version → 两个服务的 prod baseline version。
4. **[EXECUTE]** 并行 6 次 `deploy-upgrade`。
5. **[MONITOR]** 轮询全部 6 个 Ticket。
6. **[COMPLETE]** ✅

### Example 7: Batch Deploy with Service Account (服务账号批量部署)
**User**: "使用服务账号部署 svc.a、svc.b、svc.c 到环境 ppe_batch"

1. **[INIT]** Intent=BATCH_DEPLOY。
   - secret → 用户提供 ✅; env → ppe_batch ✅; 服务数 3 ≤ 30 ✅
   - `bits_env_cli service-auth --secret <secret>` → 认证成功 ✅
2. **[SEARCH]** 环境不存在。
3. **[RESOLVE]** 并行 recommend-cluster + recommend-version。
4. **[PLAN]** 表格确认：

   | # | PSM | Action | Cluster | Version | Cluster-Config | CPU:MEM |
   |---|-----|--------|---------|---------|----------------|---------|
   | 1 | svc.a | create | default | 1.0.1.810 | China-North-LF\|PPE\|default\|HL:1 | — |
   | 2 | svc.b | create | default | 1.0.1.810 | China-North-LF\|PPE\|default\|HL:1 | — |
   | 3 | svc.c | create | default | 1.0.2.903 | China-North-LF\|PPE\|default\|HL:1 | — |

5. **[EXECUTE]** 所有命令携带 `--service-auth`。
6. **[COMPLETE]** 跳过 MONITOR，输出工单汇总表。
7. **[CLEANUP]** `bits_env_cli service-auth --clear`。

### Example 8: Single Cluster with Multi-IDC Instances (单集群多机房)
**User**: "把 ecom.fulfillment.promise 部署到 ppe_test，实例分布在 HL 和 LQ 两个机房"

1. **[INIT]** 语义识别：用户说"实例分布在" → 单集群多机房模式。
2. **[RESOLVE]** 一次调用：`recommend-cluster --specify-dcs HL,LQ`
   → 1 个集群，instanceList=[HL:1, LQ:1], base_cluster_id=558427。
3. **[EXECUTE]** 一次 deploy-create：
   `--cluster-config "China-North-LF|PPE|ipv6|HL:1,LQ:1" --base-cluster-id 558427`
4. **[COMPLETE]** ✅

### Example 9: Multiple Clusters in Different IDCs (多集群不同机房)
**User**: "把 bits.env.api 部署到 ppe_test，要两个集群，一个在 LQ，一个在 HL"

1. **[INIT]** 语义识别：用户说"两个集群" → 多集群模式。
2. **[RESOLVE]** 两次调用：
   `recommend-cluster --specify-dcs LQ` → 集群 1 (amd, LQ:1)
   `recommend-cluster --specify-dcs HL` → 集群 2 (default, HL:1)
3. **[PLAN]** 先锋-跟随（同服务多集群 Create）。
4. **[EXECUTE]** 先锋 → 等待服务创建 → 跟随。
5. **[COMPLETE]** ✅

### Example 10: Deploy with Custom CPU and Memory (指定资源规格)
**User**: "用服务账号把 aweme.api.social_basic 部署到 ppe_skills_multi_idc，集群名 ugc，8核16G，实例分布在 HL、LF、LQ"

1. **[INIT]** Intent=BATCH_DEPLOY, psm=aweme.api.social_basic, env=ppe_skills_multi_idc, cluster-name=ugc, cpu-mem=8:16.
   语义识别：用户说"实例分布在" → 单集群多机房模式。
2. **[RESOLVE]** `recommend-cluster --specify-dcs HL,LF,LQ` → instanceList=[HL:1, LF:1, LQ:1], base_cluster_id=300294.
   recommend-version → version=1.0.0.3821.
3. **[EXECUTE]** `bits_env_cli deploy-create --env ppe_skills_multi_idc --psm aweme.api.social_basic --version 1.0.0.3821 --cluster-config "China-North-LF|PPE|ipv6|HL:1,LF:1,LQ:1" --cluster-name ugc --base-cluster-id 300294 --cpu-mem 8:16 --standard-env online_cn --service-auth`
4. **[COMPLETE]** 跳过 MONITOR，输出工单汇总。
5. **[CLEANUP]** `bits_env_cli service-auth --clear`。

### Example 11: Batch Deploy — Same PSM Multiple Clusters Same IDCs (同服务多集群相同机房)
**User**: "使用服务账号批量部署以下服务到 ppe_base：aweme.namek.merchant_api default 集群 LF LQ HL 4C8G，aweme.namek.merchant_api poi_task 集群 LF LQ HL 4C8G，data.life.ai_core default 集群 LF LQ HL 4C16G"

1. **[INIT]** Intent=BATCH_DEPLOY, env=ppe_base.
   - 拆解为 3 个 deploy-create 任务（2 个 PSM，其中 aweme.namek.merchant_api 有 2 个集群）
   - secret → 用户提供 ✅; 服务数 2 ≤ 30 ✅
   - `bits_env_cli service-auth --secret <secret>` → 认证成功 ✅
2. **[SEARCH]** 环境不存在。
3. **[RESOLVE]** 共 **3 次** recommend-cluster（每个集群各一次，即使参数相同）：
   - aweme.namek.merchant_api (default): `recommend-cluster --specify-dcs LF,LQ,HL` → ipv6, base_cluster_id=1529496
   - aweme.namek.merchant_api (poi_task): `recommend-cluster --specify-dcs LF,LQ,HL` → ipv6, base_cluster_id=1529496
   - data.life.ai_core (default): `recommend-cluster --specify-dcs LF,LQ,HL` → ipv6, base_cluster_id=203611152
   - 并行 recommend-version → aweme 版本 1.0.0.7618, data 版本 1.0.0.3936
4. **[PLAN]** 确认表格：

   | # | PSM | Cluster | Cluster-Config | Base Cluster | Version | CPU:MEM |
   |---|-----|---------|----------------|-------------|---------|---------|
   | 1 | aweme.namek.merchant_api | default | China-North-LF\|PPE\|ipv6\|HL:1,LF:1,LQ:1 | 1529496 | 1.0.0.7618 | 4:8 |
   | 2 | aweme.namek.merchant_api | poi_task | China-North-LF\|PPE\|ipv6\|HL:1,LF:1,LQ:1 | 1529496 | 1.0.0.7618 | 4:8 |
   | 3 | data.life.ai_core | default | China-North-LF\|PPE\|ipv6\|HL:1,LF:1,LQ:1 | 203611152 | 1.0.0.3936 | 4:16 |

   > 注意：#1 和 #2 的 cluster-config 完全相同是正常的——它们是同一服务的不同集群，通过 `--cluster-name` 区分。

   aweme.namek.merchant_api 有 2 个集群 Create → 先锋-跟随模式。
5. **[EXECUTE]**
   - Phase 1 (先锋): deploy-create aweme.namek.merchant_api `--cluster-name default` + data.life.ai_core `--cluster-name default`（两个服务互相独立，并行）
   - 等待 aweme 先锋工单中"创建服务 (Succeed)"
   - Phase 2 (跟随): deploy-create aweme.namek.merchant_api `--cluster-name poi_task`
   - 所有命令携带 `--service-auth`、`--cpu-mem`、`--base-cluster-id`
   
   先锋命令示例：
   ```
   bits_env_cli deploy-create --env ppe_base --psm aweme.namek.merchant_api --version 1.0.0.7618 --cluster-config "China-North-LF|PPE|ipv6|HL:1,LF:1,LQ:1" --cluster-name default --base-cluster-id 1529496 --cpu-mem 4:8 --standard-env online_cn --service-auth
   ```
   跟随命令示例：
   ```
   bits_env_cli deploy-create --env ppe_base --psm aweme.namek.merchant_api --version 1.0.0.7618 --cluster-config "China-North-LF|PPE|ipv6|HL:1,LF:1,LQ:1" --cluster-name poi_task --base-cluster-id 1529496 --cpu-mem 4:8 --standard-env online_cn --service-auth
   ```
6. **[COMPLETE]** 跳过 MONITOR（BATCH_DEPLOY），输出工单汇总表。
7. **[CLEANUP]** `bits_env_cli service-auth --clear`。

### Example 12: Deploy TCC Service (TCC 类型服务部署)
**User**: "在 ppe_config 环境部署一个 TCC 类型的服务 config.center.service"

1. **[INIT]** Intent=CREATE_NEW, env=ppe_config, psm=config.center.service, service-type=tcc.
   因为 service-type=tcc，不需要提取 version/branch/cluster-config/cpu-mem。
2. **[SEARCH]** `env-search --keyword ppe_config` → 环境不存在。
3. **[VALIDATE]** 校验 env 格式 ✅、psm 格式 ✅、standard-env=online_cn ✅。
   SV-12 检查：确认未携带 TCE 专有参数 ✅。
4. **[RESOLVE]** TCC 服务跳过 RESOLVE（不需要 recommend-cluster 和版本推荐流程）。
5. **[PLAN]**
   ```
   ═══════════════════════════════════════════════════
     📋 Deployment Plan
   ═══════════════════════════════════════════════════
     Target: ppe_config
     [1] CREATE (TCC) config.center.service
         Type: TCC
   ═══════════════════════════════════════════════════
   ```
6. **[EXECUTE]** `bits_env_cli tcc-deploy-create --env ppe_config --psm config.center.service --standard-env online_cn`
7. **[MONITOR]** 轮询工单至终态。
8. **[COMPLETE]** ✅
   > 提示用户：TCC 服务已创建完成。后续配置操作（创建/发布/查询配置）可使用 tcc_ref.md 中的 TCC 平台操作命令。

### Example 13: Mixed TCE + TCC Batch Deploy (混合类型批量部署)
**User**: "使用服务账号批量部署到 ppe_mixed：ecom.order.service default 集群 LF 机房（TCE），config.center.service（TCC）"

1. **[INIT]** Intent=BATCH_DEPLOY, env=ppe_mixed.
   - 拆解为 2 个 deploy 任务：
     - ecom.order.service: service-type=tce, cluster-name=default
     - config.center.service: service-type=tcc
   - secret → 用户提供 ✅; 服务数 2 ≤ 30 ✅
   - `bits_env_cli service-auth --secret <secret>` → 认证成功 ✅
2. **[SEARCH]** 环境不存在。
3. **[RESOLVE]** 仅对 TCE 服务执行：
   - ecom.order.service: `recommend-cluster --specify-dcs LF` → default, LF:1
   - ecom.order.service: 版本推荐流程 → version=2.1.0.500
   - config.center.service (TCC): 跳过 RESOLVE
4. **[PLAN]** 确认表格：

   | # | PSM | Type | Action | Cluster | Namespace | Version | Cluster-Config | CPU:MEM |
   |---|-----|------|--------|---------|-----------|---------|----------------|---------|
   | 1 | ecom.order.service | TCE | create | default | — | 2.1.0.500 | China-North-LF\|PPE\|default\|LF:1 | — |
   | 2 | config.center.service | TCC | create | — | — | — | — | — |

5. **[EXECUTE]** 两个服务可并行：
   - TCE: `bits_env_cli deploy-create --env ppe_mixed --psm ecom.order.service --version 2.1.0.500 --cluster-config "China-North-LF|PPE|default|LF:1" --standard-env online_cn --service-auth`
   - TCC: `bits_env_cli tcc-deploy-create --env ppe_mixed --psm config.center.service --standard-env online_cn --service-auth`
6. **[COMPLETE]** 跳过 MONITOR（BATCH_DEPLOY），输出工单汇总表。
7. **[CLEANUP]** `bits_env_cli service-auth --clear`。