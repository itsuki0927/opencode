---
name: bytedance-merlin
description: "Operate Merlin workflows via bytedcli: extract or resubmit Merlin job YAML, list Merlin job runs, resolve a job to trial ids, query stdout/stderr logs for Merlin jobs/trials, inspect Merlin tracking projects/runs/metrics, read `merlin quota` data for groups/clusters, run Merlin trial diagnose/local-log, and resolve tracking links from Merlin job ids. Use whenever tasks mention Merlin jobs, Merlin trials, Merlin logs, Merlin tracking, Merlin quota, Merlin console URLs, `trial.yaml`, tracking run ids, metric curves, groups, or mapping a Merlin job to tracking pages."
---

# bytedcli Merlin

## Table of Contents

- [如何调用 bytedcli](#如何调用-bytedcli)
- [When to use](#when-to-use)
- [前置条件](#前置条件)
- [Quick start](#quick-start)
- [Recommended flow](#recommended-flow)
- [Concept model](#concept-model)
- [Job flow](#job-flow)
- [Logs flow](#logs-flow)
- [Tracking flow](#tracking-flow)
- [Quota flow](#quota-flow)
- [Task examples](#task-examples)
- [Job example](#job-example)
- [Logs example](#logs-example)
- [Tracking example](#tracking-example)
- [Quota example](#quota-example)
- [Notes](#notes)
- [References](#references)

## 如何调用 bytedcli

先选择一种调用方式。下面所有示例默认直接写 `bytedcli`。

```bash
# 方式 1：直接用 npx 运行最新版
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest <command> [options]

# 方式 2：先全局安装，再直接调用 bytedcli
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npm install -g @bytedance-dev/bytedcli@latest
bytedcli <command> [options]
```

## When to use

- 从现有 Merlin job id 或 job URL 提取可再次提交的 YAML
- 重新提交本地 `trial.yaml`
- 查询 Merlin job/trial 的 stdout/stderr 日志
- 查看 Merlin tracking project / run / entity names / scalar 数据
- 根据 Merlin job run id 反查 tracking 页面链接
- 查看 `merlin quota` 下的 groups / clusters 信息
- 用 `merlin trial diagnose` / `merlin trial local-log` 处理 trial 级问题

## 前置条件

- 使用通用调用方式：`references/invocation.md`
- 先完成 `bytedcli auth login`，复用现有 SSO / ByteCloud JWT 状态
- 使用全局 `--site` 和可选的 `--vregion` 选择 Merlin 环境
- Merlin 当前不支持 `--vdc`；传入非空 `--vdc` 会直接报错
- 在 ByteDance 生产网环境下调用 i18n-tt：`export BYTEDCLI_NETWORK_PROFILE=prod` 并加 `--auth-site bytedance`

## Quick start

```bash
# 查看 Merlin 各 surface 的 site/vregion/vdc、origin 与 API Root 对应关系
bytedcli merlin job list-sites
bytedcli merlin trial list-sites
bytedcli merlin logs list-sites
bytedcli merlin tracking list-sites
bytedcli merlin quota list-sites

# Job：列表、提取、重提、停止、解析 trial ids
bytedcli merlin job list --status running
bytedcli merlin job list --queued --page-size 50
bytedcli merlin job extract --job <job-run-id>
bytedcli --site cn --vregion seed merlin job extract --job <job-run-id>
bytedcli merlin job extract --job "https://example.merlin.site/development/instance/jobs/<job-run-id>" --output ./trial.yaml
bytedcli merlin job submit --body-file ./trial.yaml
bytedcli --site i18n-bd --json merlin job submit --body-file ./trial.yaml
bytedcli merlin job stop --job <job-run-id>
bytedcli merlin job trials --job <job-run-id>

# Trial：诊断与本地日志
bytedcli merlin trial diagnose --trial-id <trial-id>
bytedcli merlin trial local-log --trial-id <trial-id> --stream stderr --tail 200

# Logs：抓取 stdout/stderr
bytedcli merlin logs get --job <job-run-id>
bytedcli merlin logs get --job "https://example.merlin.site/development/instance/jobs/<job-run-id>?trialId=<trial-id>" --stream stderr --tail 50
bytedcli merlin logs get --trial-id <trial-id> --stream both --all-instances --all

# Tracking：项目、run、指标与 job links
bytedcli merlin tracking project list --keyword demo --limit 5
bytedcli merlin tracking run get --project-name ci --run-id <run-id>
bytedcli --json merlin tracking run scalar list --project-name ci --run-id <run-id> --name train/loss,val/loss
bytedcli merlin tracking job links --job-run-id <job-run-id>

# Quota：groups、clusters
bytedcli merlin quota group list --approved-only
bytedcli merlin quota group resources --group-id 271
bytedcli merlin quota cluster list
```

## Recommended flow

### Concept model

1. `job` 是一次提交到 Merlin 的训练任务。
2. 一个 `job` 下通常有一个 `trial`，也可能有多个 `trial`。
3. 一个 `trial` 下还可能有多个 robust runs。
4. stdout/stderr 日志属于 `trial / instance / stream` 维度，且可能过期。
5. `tracking` 是另一套观测面：`run_id` 稳定唯一，`run_name` 只是人类可读名称。

### Job flow

1. 先执行 `bytedcli merlin job list-sites`，确认要访问的 `site` / `vregion`、job core route，以及 `job trials` 的 primary / fallback routes。
2. 需要确认“我提交的 jobs 排队到哪里了”时，优先执行 `merlin job list --queued --page-size 50`，再对返回 job 的 trial id 执行 `merlin trial diagnose --trial-id <trial-id>`。
3. 注意网页上的“排队中”不一定对应 job core 的 `WAITING` / `PENDING` 状态；常见形态是 job core `STARTED`，但 `meta.arnoldTrialStatus=queued`。不要只用 `merlin job list --status waiting,pending,running` 判断是否存在排队任务。
4. 用 `merlin job extract --job <job-id-or-url>` 提取 submit-ready YAML。
5. 如需重复使用，带上 `--output ./trial.yaml` 把 YAML 落盘。
6. 需要切环境时，使用全局 `--site` 和必要时的 `--vregion seed`。
7. 用 `merlin job submit --body-file ./trial.yaml` 重新提交 job。

### Logs flow

1. 先执行 `bytedcli merlin logs list-sites`，确认 logs 使用的 Streamlog API Root。
2. 已有 Merlin job id 或 job URL 时，优先用 `merlin logs get --job ...`。
3. 若 URL 已带 `trialId`，CLI 会直接使用；若只给 bare job id，CLI 会先解析一个合理的 trial。
4. 需要精确命中 Streamlog 后端查询对象时，优先用 `--pod-name <kubernetes-pod-name>`；需要跨实例时，用 `--all-instances`。
5. 默认返回 recent tail；要完整抓取时，用 `--all`。

### Tracking flow

1. 先执行 `bytedcli merlin tracking list-sites` 确认 tracking API Root。
2. 需要找 project 时，先用 `merlin tracking project list --keyword ...` 或 `project get --project-name ...`。
3. 需要看某个 run 的基础字段、config、summary 时，用 `merlin tracking run get --project-name <name> --run-id <id>`。
4. 需要导出指标名称或 scalar 序列时，用 `run entity-names` 与 `run scalar list`。
5. 只有 Merlin job run id 时，用 `merlin tracking job links --job-run-id <id>` 反查 tracking 页面链接。

### Trial and quota flow

1. 先执行 `bytedcli merlin quota list-sites` 确认 quota API Root。
2. 需要找可见 group 时，先用 `merlin quota group list`；如果只关心已批准权限，加 `--approved-only`。
3. 需要看某个 group 的按 cluster 资源信息时，用 `merlin quota group resources --group-id <group.id>`。
4. 需要看 clusters 时，用 `merlin quota cluster list`。
5. 需要从 job run 解析 trial ids 时，用 `merlin job trials --job <job-id-or-url>`；它会优先按 Arnold `custom_id = job_run_id` 枚举所有 trials，必要时再回退到 `job_run/get`。
6. 需要看某个 trial 是否卡在排队、调度、配额等 Arnold 侧诊断问题时，用 `merlin trial diagnose --trial-id <id>`；若返回空诊断，再结合 `logs get` 或 `trial local-log` 继续排查。
7. 需要抓某个 trial 的本地训练日志时，用 `merlin trial local-log --trial-id <id>`。

## Task examples

### Job example

```text
使用 bytedcli merlin job 相关技能，从
https://example.merlin.site/development/instance/jobs/<job-run-id>
提取 submit-ready YAML，并存到 ./tmp_1.yaml
```

### Queued job example

```text
用户问“我提交的 jobs 排队到哪里了”时，先确认 site / vregion，再执行：

bytedcli --site cn --vregion seed --json merlin job list --queued --page-size 50

对每个返回的 job 读取 trial id、cluster、queue、申请 GPU 数等字段，再执行：

bytedcli --site cn --vregion seed --json merlin trial diagnose --trial-id <trial-id>
```

常见误判模式：只查询 `merlin job list --status waiting,pending,running`，然后对结果里的 running trial 执行 `trial diagnose`。这会漏掉网页上显示“排队中”的 job，因为该 job 可能在 job core 里是 `STARTED`，实际排队状态在 `meta.arnoldTrialStatus=queued`。如果因此拿 running trial 做诊断，通常只会得到 `DiagnosticCode=0` / `QueueInfo=null`，并错误判断为没有排队或配额问题。

### Trial example

```text
使用 bytedcli merlin trial 相关技能，看看
https://example.merlin.site/development/instance/jobs/<job-run-id>?tabState=run_info&trialId=<trial-id>
是什么状态，有没有出什么问题。
```

### Logs example

```text
使用 bytedcli merlin logs 相关技能，从
https://example.merlin.site/development/instance/jobs/<job-run-id>?tabState=run_info&trialId=<trial-id>
拉取 pod_name 是 trial-<trial-id>-trialrun-<trial-id>-executor-7 那个实例上最末尾的日志：stdout 和 stderr 各 150 行，并根据日志分析程序运行是否正常。
```

### Tracking example

```text
使用 bytedcli merlin tracking 相关技能，从
site：cn
vregion：seed
project_name：<awesome-project-name>
run_name：<awesome-run-name>
的 trial 中，把所有名字 pattern 是 "train/*" 的曲线拖下来。
```

### Quota example

```text
使用 bytedcli merlin quota 相关技能，查询当前账号可见的 groups，按空闲 GPU 数量由多到少排序，做成表格输出。
```

## Notes

- Merlin 使用全局 `--site` 和可选的 `--vregion` 选择 API Root；`list-sites` 默认展示 `Site | VRegion | VDC | Remark | Origin | API Root`。其中 `job list-sites` 还会额外展示 `Job Core API Root`、`Job Trials API Root` 和 `Job Trials Fallback API Root`
- 当前 Merlin 支持的 canonical site 是 `cn`、`i18n-bd`、`i18n-tt`、`eu-ttp`、`us-ttp-bdee`、`us-ttp-usts`
- 只有 `cn` 和 `i18n-bd` 支持 `--vregion seed`
- `job extract --job <job-run-id>` 与 `logs get --job <job-run-id>` 使用当前全局 Merlin 环境；传入完整 URL 时，以 URL 自身 host 为准
- `trial list-sites` 与 `quota list-sites` 当前展示的是同一套 Arnold root 映射
- `logs list-sites` 展示的是 Streamlog API Root：`${origin}/api/training/merlin_job/log/streamlog`
- `tracking list-sites` 展示的是 `${origin}/open`；`run scalar list` 会额外读取 `${origin}/open/tracking`
- `quota group list` 返回的是 membership；`group resources --group-id` 需要传 `group.id`
- `trial diagnose` 更偏 Arnold 侧的排队、调度、配额诊断；若没有命中这类问题，后端可能只返回 `DiagnosticCode: 0` 和空的 `DiagnosticInfo`
- 需要稳定机器可读输出时，优先使用 `bytedcli --json merlin ...`

## References

- `references/merlin.md`
- `references/invocation.md`
- `references/troubleshooting.md`
