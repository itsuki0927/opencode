# 配置文件参考

## eden.monorepo.json（主配置）

EMO 项目的核心配置文件，位于仓库根目录。

### 主要字段

**版本锁定：**

- `edenMonoVersion`：锁定 `@ies/eden-monorepo` 版本
- `config.pnpmVersion`：锁定 pnpm 版本

**Workspace 注册（二选一）：**

- `packages`：逐个注册子项目（数组）
- `workspaces`：glob 表达式批量注册

**构建缓存：**

- `config.cache`：配置影响缓存 hash 的输入（环境变量、文件、运行时命令）和需要保存的输出

**脚本优先级：**

- `config.scriptName.start`：`emo start` 查找的脚本顺序，默认 `["build:watch", "dev", "start", "serve"]`
- `config.scriptName.build`：`emo build` 查找的脚本，默认 `["build"]`
- `config.scriptName.test`：`emo test` 查找的脚本，默认 `["test"]`

**Checker（规范检查）：**

- `dependencyVersionCheck`：依赖版本一致性检查
- `circularDependenciesCheck`：循环依赖检查
- `phantomDependenciesCheck`：幻影依赖检查
- `projectReferencesCheck`：TypeScript 项目引用检查

大多数 checker 支持 `autofix`。

**基建目录（折叠模式）：**

- `infraDir`：将原本在根目录的基建资源折叠到指定子目录（如 `"infra"`），减少根目录噪音和幻影依赖风险。折叠后的目录结构：
  ```
  ├── eden.monorepo.json
  ├── infra/                  ← infraDir
  │   ├── package.json        ← 基建依赖（eslint, commitlint 等）
  │   ├── node_modules/
  │   ├── pnpm-lock.yaml
  │   ├── .npmrc
  │   ├── .pnpmfile.cjs
  │   ├── .changeset/
  │   ├── .commitlintrc.js
  │   ├── git-hooks/
  │   └── patches/
  ├── packages/
  └── ...
  ```
  配置 infraDir 后，使用 `emox` 运行 `${infraDir}/node_modules/.bin` 下的工具

**发布：**

- `publishTool`：默认 `"changesets"`
- `publishConfig`：发布通知等配置

## eden.mono.workspace.json（子项目配置）

放在子项目目录中，用于覆盖主配置中的全局设置（如缓存配置）。

## eden.mono.pipeline.json（流水线配置）

SCM 构建流水线配置，定义子项目与 SCM 仓库的映射关系。

## eden.mono.config.js（动态配置）

JS 格式的动态配置，适用于需要运行时逻辑的场景。

## .npmrc

pnpm/npm 的 registry 和行为配置。常见配置：

```ini
registry=https://bnpm.byted.org
strict-peer-dependencies=false
save-prefix=''
link-workspace-packages=true
```

## .pnpmfile.cjs

pnpm 的 hook 文件，可在安装时修改依赖解析行为。

---

## 原始文档

- eden.monorepo.json：<https://emo.bytedance.net/config/eden-monorepo-json.md>
- eden.mono.workspace.json：<https://emo.bytedance.net/config/eden-mono-workspace-json.md>
- eden.mono.pipeline.json：<https://emo.bytedance.net/config/eden-mono-pipeline-json.md>
- eden.mono.config.js：<https://emo.bytedance.net/config/eden-mono-config-js.md>
- .npmrc：<https://emo.bytedance.net/config/npmrc.md>
- .pnpmfile.cjs：<https://emo.bytedance.net/config/pnpmfile-cjs.md>
