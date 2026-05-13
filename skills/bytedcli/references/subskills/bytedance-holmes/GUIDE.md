---
name: bytedance-holmes
description: "Manage Holmes TrustPress tasks, ByteCore C++ coredump analysis, and code-review ticket info via bytedcli. Invoke when tasks mention TrustPress、TikDiff、压测任务、Holmes、trust-press、tanker ID、创建压测、查可用 pod、压测结果查询、ByteCore、coredump、崩溃分析、crash dump、SIGSEGV、frames_hash_id、code-review、ticket-detail、Change Type、MR Checks."
---

# bytedcli Holmes

## 工具适用场景

- 在本地电脑上使用 bytedcli 访问 CN 和 RoW 的 Holmes 工具
- 在 CN CloudIDE 上使用 bytedcli 访问 CN Holmes 工具
- 暂不支持在 CN CloudIDE 访问 RoW Holmes 工具

## 如何调用 bytedcli

先选择一种调用方式。下面所有示例默认直接写 `bytedcli`。

```bash
# 方式 1：直接用 npx 运行最新版
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest <command> [options]

# 方式 2：先全局安装，再直接调用 bytedcli
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npm install -g @bytedance-dev/bytedcli@latest
bytedcli <command> [options]
```

- 使用 `npx` 时，把后文示例里的 `bytedcli` 替换成 `NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest`
- 已全局安装时，直接按后文示例执行 `bytedcli ...`

## Authentication
抖音业务线与 TikTok 业务线用户认证鉴权上有差异，需要注意区分。

### 抖音业务线认证
```bash
bytedcli auth login --session
```
扫码完成后，后续命令会自动通过 `sso.bytedance.com` 完成 CAS 认证，无需重复操作。
在 CN CloudIDE 上没有浏览器可用，可以手动复制浏览器 cookie 设置环境变量 ```export BYTEDCLI_HOLMES_COOKIE="<cookie>"```。

### TikTok 业务线认证
```bash
bytedcli --site i18n auth login --session --session-method interactive-browser
```

## When to use

### TrustPress

- 查询 TrustPress 压测任务详情（任务类型、创建人、成功/失败数、成功率等）
- 获取压测任务的 Test Parameters（AB 参数、方法配置）
- 通过 tanker ID 查看压测结果
- 创建 TrustPress deploy-mode 压测任务
- 列出指定服务的可用 pod（空闲实例）

### TikDiff

- 创建 TikDiff 引流、压测、diff 任务：
  - 1）引流到指定 CloudIDE IP:Port；
  - 2）基于 SCM 版本/Git branch 分支/Git commit 等创建引流任务，在远程自动编译、部署服务后自动引流一条龙；
- 查询 TikDiff 引流、压测、diff 任务的报告详情；
- 上述引流任务创建既支持单机引流，又支持多机引流或多实例部署引流

### ByteCore

- **C++ coredump 聚合查询**（`holmes bytecore search --psm <psm>`）：当线上出现崩溃（SIGSEGV / OOM / 其它 signal）时，按 `frames_hash_id` 聚合同类崩溃，查看各独立签名的发生次数、涉及的 version / idc / cluster / env、崩溃调用栈、LLM 归因结论。支持按 `--env / --cluster / --version / --idc / --zone / --signum / --reason` 等维度过滤，`--with-frames` 可带回完整调用栈。需要 BDSSO session（首次使用先 `bytedcli auth login --session`）。

### Code Review

- **MR code-review ticket 信息**（`holmes code-review get --url <mr_url>`）：从 GitLab MR URL 一步拿到 Holmes ticket 的 Change Type、Ticket Status、Reviewers、IDCs、以及分组 Checks（diff / release\_manager\_tested / compatibility / other）的状态表;blocking failure 单独高亮。对应页面 `https://holmes.tiktok-row.net/code-review/ticket-detail`。同时支持 `--repo <group/project> --mr-id <n>` 和 `--no-include-checks`(只拉 header)。

## Quick start
### TrustPress

```bash
# 查看压测任务详情
bytedcli holmes trust-press get --tanker-id 106092

# 列出可用 pod
bytedcli holmes trust-press pod list --service-name <svc> --region ttp

# 创建压测任务（pod 参数省略时交互选择）
bytedcli holmes trust-press create \
  --service-name <svc> --region ttp --qps 10 --branch master

# JSON 输出（适合脚本消费）
bytedcli --json holmes trust-press get --tanker-id 106092
                               # 查可用 change_type 等枚举
```

### TikDiff

```bash
# 创建引流、压测、diff 任务
bytedcli holmes tikdiff create --case-id 2 --endpoints '[fd00:ffff:ffff:69::7a]:8080' # for CN Holmes TikDiff
bytedcli --site i18n holmes tikdiff create --case-id 1 --endpoints '[fdbd:dccd:cde2:1701:d425:bcd6:c169:ae25]:53085' # for RoW Holmes TikDiff

bytedcli --json holmes tikdiff get --task-id 2493426  # for CN Holmes TikDiff
bytedcli --json --site i18n holmes tikdiff get --task-id 2503983 # for RoW Holmes TikDiff

```

### ByteCore

```bash
# 查看 ByteCore 聚合查询结果
bytedcli holmes bytecore search --psm aweme.recommend.feed_rank
bytedcli --site i18n holmes bytecore search --psm tiktok.recommend.sort_cpp
```

### CodeReview

```bash
# 查 code-review ticket + checks(Change Type、Reviewers、Checks 汇总)
bytedcli holmes code-review get --url https://code.byted.org/tiktok-plus/tiktok_sort/merge_requests/3984
bytedcli holmes code-review get --repo tiktok-plus/tiktok_sort --mr-id 3984
bytedcli holmes code-review get --url <mr_url> --no-include-checks   # 只要 header
bytedcli holmes code-review enums   
```

## Notes

- `--tanker-id` 对应 TrustPress 页面 URL 中的 `tankerId` 参数。
- 认证通过 BDSSO CAS 流程自动完成，需要先执行 `bytedcli auth login --session` 获取 SSO session；或通过 `BYTEDCLI_HOLMES_COOKIE` 环境变量注入 cookie。
- `get` 输出包含 Task Type、Task ID、Service Name、Creator、Create/Start/End Time、Success/Failure Count、Success Rate 和 Test Parameters；JSON 模式额外返回 `deploy_info`、`metric_counters`、`raw`。
- `create` 的 pod 参数（`--ip`/`--port`/`--instance-shard-id`/`--instance-name`）省略时在 TTY 中交互选择；非 TTY 场景（Agent、CI）需先运行 `pod list` 获取后显式传入。
- `pod list` 默认只显示空闲 pod，`--all` 显示全部。
- `code-review get` 接受 GitLab MR URL 或 Holmes ticket-detail URL，也可改用 `--repo <group/project> --mr-id <n>`；默认同时拉 `/openapi/mr_ticket_meta_status`（header）+ `/ticket/{id}/check_info`(checks)，加 `--no-include-checks` 只拉 header；JSON 模式里 `check_summary.by_status` 是状态计数,`check_summary.blocking_failures` 是 block=true 且 status 为 failed/error/timeout 的列表,`check_groups[].checks[]` 保留每条 check 的原始字段。

## References

- [holmes.md](./references/holmes.md)
- [invocation.md](./references/invocation.md)
- [troubleshooting.md](./references/troubleshooting.md)

