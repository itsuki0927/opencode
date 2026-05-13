---
name: scm
description: 内部 SCM 系统统一交互入口。负责仓库资产查询、多维度版本状态追踪与依赖分析、多版本差异对比（配置/环境变量/构建环境）、发布版本创建，以及构建日志的拉取。当用户询问 SCM 仓库详情、排查发布差异、追踪构建状态或执行打包发布流程时使用此技能。
---

<!-- @telemetry:start -->
> **[TELEMETRY — MANDATORY]** Silent. Never show output to the user.
> On start: `sh "./.ai-extension/span_invoke_start.sh" 2>/dev/null &`
> On end: `sh "./.ai-extension/span_invoke_end.sh" "success" 2>/dev/null &`
> Replace `"success"` with `"error"`, `"abort"`, `"timeout"`, or `"skipped"`. Optionally add a message as 2nd argument.
<!-- @telemetry:end -->


# SCM 管理工具集

本 skill 提供一组与内部 SCM（Source Control Management）系统交互的能力，覆盖仓库查询、版本信息、版本差异对比、发布版本以及构建日志拉取。

## 适用场景

- 查询仓库信息（按 ID / 名称）
- 查询版本详情、版本状态、版本依赖、版本列表
- 对比两个版本的配置 / 环境变量 / 构建环境差异
- 创建新版本（需要鉴权）
- 拉取特定版本的构建日志

## 入口与目录结构

本 skill 的入口文件为本目录下的 `SKILL.md`，支持文件包括：

- `scripts/entry.py`：命令行入口
- `scripts/tools.py`：业务封装（参数校验、组合调用）
- `scripts/client.py`：HTTP 客户端（超时、错误处理、可配置 base_url）
- `scripts/filters_config.py`：输出字段过滤规则配置
- `scripts/__init__.py`：包初始化文件
- `scripts/requirements.txt`：Python 依赖列表
- `references/api.md`：命令参数参考
- `references/fields.md`：Repo / Version 字段说明
- `references/enums.md`：常见枚举值说明

## 使用方式（CLI）

所有工具通过 `scripts/entry.py` 暴露为命令行接口：

```bash
python3 scripts/entry.py -h
```

### 示例

获取仓库信息：

```bash
python3 scripts/entry.py get_repo --repo_name "your/repo/name"
```

创建新版本：

```bash
python3 scripts/entry.py create_version \
  --repo_name "your/repo/name" \
  --branch_name "main" \
  --type "online"
```

获取构建日志：

```bash
python3 scripts/entry.py get_build_log \
  --repo_name "your/repo/name" \
  --version_number "1.0.0.1" \
  --step_name "building"
```

## 认证与配置

本 skill 不在代码中内置任何 Token，依赖环境变量进行配置。

- `SCM_JWT_TOKEN`：访问需要鉴权的 SCM API（例如 `create_version`、`get_version_diff`）。可通过下方 Skills CLI 获取。
- `SCM_BASE_URL`：SCM 服务地址（默认 `https://scm.byted.org`）
- `BYTEBUILD_BASE_URL`：构建服务地址（默认 `https://bytebuild-nightly.byted.org`）
- `SCM_HTTP_TIMEOUT_SECONDS`：请求超时时间（秒）（默认 `10`）

## Skills CLI

飞书SSO登录获取JWT（字节云/Codebase），用于调用内部API鉴权。

`export npm_config_registry=https://bnpm.byted.org/`

字节云 JWT:`npx -y skills get-jwt`｜Codebase:`npx skills get-codebase-jwt`｜Help:`npx skills -h`

Security: JWT敏感；未明确要求勿回显原Token。

## 依赖

```bash
pip install -r scripts/requirements.txt
```

## 参数参考

完整参数说明见 API 参考手册（`references/api.md`），字段与枚举说明见 `references/fields.md` 和 `references/enums.md`。
