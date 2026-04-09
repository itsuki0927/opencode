---
name: emo-docs
description: EMO monorepo CLI 工具使用指南。当项目中存在 eden.monorepo.json 或 pnpm-lock.yaml 时，必须使用 emo 命令而非 pnpm 命令来管理依赖、构建和开发。任何涉及依赖安装（install）、添加（add）、删除（remove）、构建（build）、启动（start）、测试（test）、发布（publish）的操作都应使用此 skill。即使看到 pnpm-lock.yaml，也要优先检查是否为 EMO 项目。
---

# EMO CLI Monorepo 工具指南

EMO 是公司内部的 monorepo 管理工具，底层基于 pnpm，提供拓扑构建、workspace 管理、构建缓存等高级能力。

## 核心规则

**EMO 项目的标志是根目录存在 `eden.monorepo.json` 文件。** 即使项目中同时存在 `pnpm-lock.yaml`（EMO 底层使用 pnpm），也必须使用 `emo` 命令而非 `pnpm` 命令。直接使用 pnpm 会绕过 EMO 的 monorepo 管理逻辑，导致依赖安装不完整、构建顺序错误等问题。

检测方式：

```bash
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
ls "$REPO_ROOT/eden.monorepo.json" 2>/dev/null
```

## Scope

- **依赖管理**: `emo install`, `emo add`, `emo remove`(别名 `rm`), `emo update`
- **本地开发**: `emo start`, `emo build`, `emo test`, `emo run`, `emo exec`
- **清理重置**: `emo clean`, `emo reset`
- **版本发布**: `emo add-changeset`(别名 `ac`), `emo version`, `emo publish`
- **Workspace**: `emo create`, `emo register`, `emo check`
- **CI/CD**: `emo pipeline`, `emo scm`
- **配置**: `eden.monorepo.json`, `eden.mono.workspace.json`, `eden.mono.pipeline.json`, `.npmrc`

## 命令映射：pnpm → emo

在 EMO 项目中，**永远使用 emo 命令**：

| 不要使用 (pnpm)                   | 应该使用 (emo)                                | 说明         |
| --------------------------------- | --------------------------------------------- | ------------ |
| `pnpm install`                    | `emo install`                                 | 安装依赖     |
| `pnpm add <pkg>`                  | `emo add <pkg>`                               | 添加依赖     |
| `pnpm remove <pkg>`               | `emo remove <pkg>` (别名 `emo rm`)            | 移除依赖     |
| `pnpm update <pkg>`               | `emo update <pkg>`                            | 更新依赖     |
| `pnpm run build`                  | `emo build` 或 `emo run build`                | 构建项目     |
| `pnpm run start` / `pnpm run dev` | `emo start`                                   | 启动开发服务 |
| `pnpm run test`                   | `emo test`                                    | 运行测试     |
| `pnpm run <script>`               | `emo run <script>`                            | 执行脚本     |
| `pnpm exec <cmd>`                 | `emo exec <cmd>`                              | 执行命令     |
| `pnpm publish`                    | `emo publish`                                 | 发布 NPM 包  |
| `pnpm patch`                      | `emo rpm patch`                               | 打补丁       |
| `pnpm patch-commit`               | `emo rpm patch-commit`                        | 提交补丁     |
| `pnpm why / list`                 | `emo run-pnpm why / list` (别名 `emo rpm`)    | 查询依赖     |
| —                                 | `emo clean`                                   | 清理到 clone 后状态 |
| —                                 | `emo reset`                                   | 重置项目     |

> 需要直接调用 pnpm 时，使用 `emo run-pnpm`（别名 `emo rpm`），它会调用 `eden.monorepo.json` 中 `pnpmVersion` 指定版本的 pnpm。

## 常用工作流

### 日常开发

1. `emo install` 安装依赖
2. `emo start <workspace>` 启动开发（自动查找 `build:watch` → `dev` → `start` → `serve`）
   - 多项目联调：`emo start <workspace> --dependencies` 按拓扑顺序自动启动所有依赖项目的 watch
3. `emo build <workspace>` 构建（自动处理依赖拓扑）
4. `emo test <workspace>` 运行测试

### 发布流程

1. `emo add-changeset` — 生成 changeset 文件
2. `emo version` — 消耗 changeset，更新版本号和 CHANGELOG
3. `emo publish` — 发布包（自动创建 git tag）

包的 `private` 不能为 `true` 才可发布。

### Workspace 管理

1. 检查注册模式（三选一，不可混用）：手动维护 `pnpm-workspace.yaml`（推荐）、`eden.monorepo.json` 的 `packages` 字段逐个注册、或 `workspaces` 字段 glob 批量注册
2. `emo create` 创建子项目（前提：需先 `emo add @byted/create@latest -D --infra`）/ `emo register` 注册已有目录
3. 删除 workspace：删源码 → `eden.monorepo.json` 移除注册 → `emo install`

### 最佳实践

- **优先用 `--filter`**：`emo build --filter <pkg>` 避免全量构建
- 声明所有依赖，避免幻影依赖
- 在 `eden.monorepo.json` 中锁定 `pnpmVersion`
- 开启 `workspaceCheck` 进行规范治理
- 使用 `emox` 运行 `${infraDir}/node_modules/.bin` 下的工具

## 参考文档

详细文档在 reference 文件中，按需读取：

- `./references/workspace-management.md` — workspace 创建/删除/注册、`--filter` 语法、`emo check`
- `./references/version-release.md` — changeset → version → publish 完整流程
- `./references/cicd.md` — CI/CD 流水线、SCM 构建（`emo scm`、`emo pipeline`）
- `./references/config.md` — `eden.monorepo.json` 字段详解、各配置文件
- `./references/local-dev.md` — 产物开发 vs 源码开发、多项目联调、连环 watch
- `./references/troubleshooting.md` — 常见问题排查

## FAQ

| 问题 | 回答 |
| ---- | ---- |
| `emo build` vs `emo run build`？ | `emo build` 选单一入口+依赖链；`emo run build` 在项目集合中执行，用 `--filter` 控制范围 |
| `emo start` 循环构建？ | 子项目 start script 不要写 `emo start`，改为实际构建工具命令 |
| `emo start` 卡住？ | 设置 `EDEN_MONO_IS_STREAM=1` 开启流式日志 |
| 类型声明报错？ | 重启 TS Server：`Cmd+P` → `>restart` → `TypeScript: Restart TS Server` |
| 调试外部包？ | `package.json` 中用 `"link:/path"` + `emo install` |
| 依赖版本不一致？ | `emo check` 检查 + `eden.monorepo.json` 的 `dependencyVersionCheck` / `preferedVersions` 配置 |
| 如何关闭依赖预构建？ | `emo start --no-build-deps` 或 `emo run start --filter "<pkg>"` |
| 如何用 pnpm patch？ | `emo rpm patch <pkg>` → `emo rpm patch-commit <folder>` |
| `.npmrc` 放哪里？ | `${infraDir}/.npmrc`（如果配了 infraDir） |
| 如何修改 pnpm 版本？ | `eden.monorepo.json` 的 `config.pnpmVersion` 字段 |

更多问题见 `./references/troubleshooting.md`。

## 外部链接

- EMO 官方文档：<https://emo.bytedance.net/llms.txt>
- 命令速查：<https://emo.bytedance.net/tutorial/introduction/cheat-sheet.md>
- 配置参考：<https://emo.bytedance.net/config/eden-monorepo-json.md>
- FAQ：<https://emo.bytedance.net/faq/dev-build-test.md>
