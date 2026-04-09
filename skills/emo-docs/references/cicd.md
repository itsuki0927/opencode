# CI/CD 操作

## emo scm

SCM 构建的快捷命令，等价于 `emo pipeline --scene scm`。用于在 SCM 环境中构建 monorepo 子项目，让 monorepo 项目的部署体验和普通项目一样简单。

```bash
# SCM 环境自动执行（通过环境变量 CUSTOM_REPO_NAME 指定子项目）
emo scm

# 本地调试 SCM 构建（交互式选择子项目）
emo scm

# 指定子项目
BUILD_REPO_NAME=xxx emo scm
```

`emo scm` 自动处理：

- 查找子项目入口
- 安装依赖
- 按拓扑顺序构建依赖
- 恢复 Node 依赖
- 执行子项目构建脚本
- 整理和拷贝产物

配置文件：`eden.mono.pipeline.json`

### 本地模拟 SCM 构建

排查"SCM 构建失败但本地成功"的问题：

```bash
emo clean      # 清理到 clone 后的状态
emo scm        # 模拟 SCM 的局部安装条件
```

## emo pipeline

通用的 CI/CD 流水线命令，支持多种场景。

```bash
# GitLab CI
emo pipeline --scene gitlab

# Codebase CI（影响范围构建/测试）
emo pipeline --scene codebase

# SCM 构建
emo pipeline --scene scm

# 本地运行
emo pipeline --scene local
```

### 主要参数

| 参数 | 说明 |
|---|---|
| `--scene` | 场景：`gitlab`、`codebase`、`scm`、`local` |
| `--trigger-branch` | 触发类型：`push`、`create`、`submit`、`abandon` |
| `--code-diff` / `--no-code-diff` | 是否计算影响范围（仅 gitlab/codebase） |
| `--skip-cache` | 跳过构建缓存 |
| `--recover-deps` | 恢复依赖（仅 scm） |
| `--filter` | 过滤 workspace（仅 gitlab/codebase） |
| `--exit-when-fail` | 遇到失败是否中断（默认 true） |

---

## 原始文档

- emo pipeline：<https://emo.bytedance.net/cli/cicd/pipeline.md>
- emo scm：<https://emo.bytedance.net/cli/cicd/scm.md>
- Codebase CI 教程：<https://emo.bytedance.net/tutorial/internal-platform/codebase-ci.md>
- SCM 构建教程：<https://emo.bytedance.net/tutorial/internal-platform/scm.md>
