# 本地开发模式

## 产物开发 vs 源码开发

EMO 项目有两种开发模式，理解它们的区别很重要。

### 产物开发（依赖 dist）

默认模式。子项目 A 依赖 B 时，使用的是 B 的构建产物（`dist/`）。

**多项目联调时需要连环 watch：**
假设依赖链 `app → component → util`：

1. 先在 `util` 目录启动 watch（子项目内执行其 start script）
2. 再启动 `component` 的 watch
3. 最后启动 `app` 的 dev

或者使用 EMO 的一键启动：

```bash
emo start app --dependencies
```

这会按拓扑顺序自动启动所有依赖项目的 watch。

也可以多开终端窗口在各子项目目录中分别执行其 start script（注意启动顺序）。

### 源码开发（依赖 src）

通过修改构建配置（如 webpack/Rspack 的 resolve），让 app 直接引用和 watch 依赖包的源码，而非 dist 产物。

**优点：**只需单开一个 start，修改任意依赖包源码都会自动触发重新构建。

**缺点：**维护成本较高，需要配置构建工具的 resolve 规则。

选择建议：

- 依赖关系简单 → 产物开发 + 多开终端
- 依赖关系复杂且团队有工程能力 → 源码开发

## emo start 脚本查找优先级

`emo start` 默认按顺序查找子项目的脚本：`build:watch` → `dev` → `start` → `serve`

可在 `eden.monorepo.json` 的 `config.scriptName.start` 中自定义。

## 流式日志

EMO 默认分块输出日志（一个包构建完整后才输出），如果某个包构建慢导致看起来"卡住"：

```bash
EDEN_MONO_IS_STREAM=1 emo start
```

---

## 原始文档

- 本地开发、构建和单测：<https://emo.bytedance.net/tutorial/basic/local-dev-build-test.md>
- 基于源码开发：<https://emo.bytedance.net/tutorial/best-practices/source-code-development.md>
- 多项目级联开发：<https://emo.bytedance.net/tutorial/best-practices/workspace-dev.md>
- emo start：<https://emo.bytedance.net/cli/local-development/start.md>
- emo build：<https://emo.bytedance.net/cli/local-development/build.md>
