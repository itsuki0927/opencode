---
name: bytedance-tools
description: "Router skill for bytedcli (ByteDance internal CLI). Use when tasks mention bytedcli, SSO/auth, TCE/TOS/Netlink/Neptune, RDS, TCC, SCM, Cloud Docs, ByteTech, Cloud Ticket, ENV, Overpass, APM, BAM, Log, Cache, Hive, DataLeap, BMQ, Kafka, BITS, DKMS, KMS v2, IAM, data encryption keys, dev tasks, pipelines, releases, or internal tech articles. Routes to subskills by domain and provides common execution patterns with --json output and help handling."
---

# ByteDance Tools (bytedcli) - 总入口

## When to use

- 用户提到 bytedcli 或 ByteDance 内部工具
- 需要在 RDS/TCC/TCE/TOS/Netlink/Neptune/SCM/Codebase/Cloud Docs/ByteTech/Cloud Ticket/ENV/Overpass/APM/BAM/Log/Cache/Hive/BMQ/DKMS/KMS v2/IAM 之间路由
- 需要在 TOS（对象存储）相关能力之间路由
- 需要搜索 Hive/Clickhouse/Doris 数据资产或查看表 schema
- 需要搜索 ByteTech 技术文章、查看热门/最新/榜单，或抓取挂载飞书文档的技术文章正文
- 需要管理数据加密密钥（DKMS/KMS v2）或查询员工信息（IAM）
- 默认执行优先级按 `CLI > Skill > MCP` 理解；当前 skill 主要用于路由与补充约束，不替代直接 CLI 调用

## 前置条件

- 按通用调用方式执行命令（含内网 registry）：`skills/bytedance-tools/references/invocation.md`
- 需要鉴权的命令先登录：`NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest auth login`

> 下面示例直接使用内部源 npx 前缀（与 invocation 文档一致）。

## Quick start

```bash
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest --help
NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest --json auth status
```

## 领域路由（渐进式加载）

- **认证/SSO**：`bytedance-auth`
- **Codebase**：`bytedance-codebase`
- **RDS**：`bytedance-rds`
- **TCC**：`bytedance-tcc`
- **TCE**：`bytedance-tce`
- **TOS**：`bytedance-tos`
- **Netlink**：`bytedance-netlink`
- **Neptune**：`bytedance-neptune`
- **SCM**：`bytedance-scm`
- **Cloud Docs**：`bytedance-cloud-docs`
- **ByteTech**：`bytedance-bytetech`
- **Cloud Ticket**：`bytedance-cloud-ticket`
- **ENV**：`bytedance-env`
- **Overpass**：`bytedance-overpass`
- **APM**：`bytedance-apm`
- **BAM**：`bytedance-bam`
- **Log**：`bytedance-log`
- **Cache**：`bytedance-cache`
- **Hive (DataLeap)**：`bytedance-hive`
- **BMQ (Kafka)**：`bytedance-bmq`
- **BITS (研发任务)**：`bytedance-bits`
- **Settings**：`bytedance-settings`
- **DKMS (数据密钥)**：`bytedance-dkms`
- **KMS v2 (密钥管理 v2)**：`bytedance-kmsv2`
- **IAM (身份管理)**：`bytedance-iam`

## Notes

- 缺少必填参数会输出完整帮助信息
- 需要机器可读输出时加 `--json`
- `--json` 是全局参数，必须放在子命令前，例如 `NPM_CONFIG_REGISTRY=http://bnpm.byted.org npx -y @bytedance-dev/bytedcli@latest --json auth status`

## References

- `skills/bytedance-tools/references/invocation.md`
- `skills/bytedance-tools/references/troubleshooting.md`
- 各领域 references 文件
