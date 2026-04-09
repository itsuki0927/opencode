# Workspace 管理

## 核心概念

Workspace 是 EMO monorepo 中依赖安装、构建、测试和部署的最小管理单元。

## 注册方式（三选一，不可混用）

1. **手动维护 `pnpm-workspace.yaml`**（推荐）
2. **`eden.monorepo.json` 的 `packages` 字段**：逐个注册
3. **`eden.monorepo.json` 的 `workspaces` 字段**：glob 表达式批量注册

使用 glob 方式时，每个 workspace 的独立配置通过 `eden.mono.workspace.json` 管理。

## 创建子项目

```bash
# 交互式创建（选择模板）
emo create

# 跳过依赖安装
emo create --skip-install

# 使用自定义 Generator（v3.7.1+）
emo create --generator <name>

# 初始化 monorepo（非子项目）
npx @byted/create@latest --emo
```

前提：需要在 infra 或根目录安装 `@byted/create`：
```bash
emo add @byted/create@latest -D --infra
```

## 注册已有目录

```bash
emo register
```

## 删除 workspace

1. 删除源码目录
2. 从 `eden.monorepo.json` 中移除注册
3. 执行 `emo install` 更新 lockfile

## --filter 过滤语法

`--filter` 参数支持灵活的 workspace 选择，可用于 `emo run`、`emo test`、`emo install` 等大多数命令：

| 语法 | 含义 | 示例 |
|---|---|---|
| 包名 | 精确匹配 | `--filter "@scope/app"` |
| 通配符 | 模糊匹配 | `--filter "@scope/p*"` |
| `...` 后缀 | 包含依赖 | `--filter "@scope/app..."` |
| `...` 前缀 | 包含被依赖者 | `--filter "...@scope/lib"` |
| `^...` | 仅依赖（不含自身） | `--filter "^...@scope/app"` |
| `...^` | 仅被依赖者（不含自身） | `--filter "@scope/lib...^"` |
| 路径 | 目录匹配 | `--filter './packages/'` |
| git diff | 变更包 | `--filter "[origin/master]"` |
| `!` 前缀 | 排除 | `--filter '!@scope/app'` |

过滤器可组合使用，多个 `--filter` 参数取并集。

## 规范检查

```bash
# 执行所有 checker
emo check

# 自动修复
emo check --autofix

# 输出 JSON 报告
emo check --json-output-file result.json
```

支持的检查项：依赖版本一致性、循环依赖、幻影依赖、项目引用等。配置在 `eden.monorepo.json` 的 checker 字段中。

---

## 原始文档

- Workspace 管理：<https://emo.bytedance.net/tutorial/basic/workspace-management.md>
- emo create：<https://emo.bytedance.net/cli/workspace-management/create.md>
- emo register：<https://emo.bytedance.net/cli/workspace-management/register.md>
- emo check：<https://emo.bytedance.net/cli/workspace-management/check.md>
