# 常见问题排查

## 依赖相关

### IDE 类型提示报错 "找不到相关类型声明"

`emo install` 或 `emo build` 后 ts-server 不会监听 node_modules 变化，需手动重启：
`Cmd+P` → 输入 `>restart` → 选择 `TypeScript: Restart TS Server`

也可以配置 project reference 让类型在内存中构建。

### 调试外部 NPM 包

不推荐 `pnpm link`（上手成本高）。推荐修改 `package.json` 版本声明为 `link:` 路径：

```json
{
  "devDependencies": {
    "@some/pkg": "link:/path/to/local/package"
  }
}
```

然后执行 `emo install`。这是 pnpm 原生支持的功能。

### 依赖版本不一致

多个子项目使用同一个库的不同版本会导致兼容性问题和包体膨胀。使用 `emo check` 检查，通过 `eden.monorepo.json` 的 `dependencyVersionCheck` 和 `preferedVersions` 配置统一管理。

## 构建相关

### emo start 循环构建

子项目 `package.json` 的 start script 不应是 `emo start`，否则会死循环。应改为实际构建工具命令（如 `rspack serve`、`webpack serve`）。

如果曾使用 `CoraWebpackV5Builder` 接管 Eden V2 构建，需要在 `eden.monorepo.json` 里删除对应 builder 配置。

### emo start 关闭依赖预构建

```bash
# 方法 1：命令行参数
emo start --no-build-deps

# 方法 2：使用 emo run 自行控制
emo run start --filter "@scope/app"

# 方法 3：删除依赖包的 build 脚本（如果始终被源码依赖）
```

也可以写 EMO 插件在 `buildProjectGraph.addDependencies` hook 中修改依赖图。

### emo build vs emo run build

- `emo build`：单一入口，自动构建依赖链 + 自身（≈ `emo run build --filter <pkg>...`）
- `emo run build`：在项目集合中执行 build 脚本，默认所有子项目，用 `--filter` 控制范围
- `npm/pnpm run build`：仅在当前子项目目录下运行，不处理依赖

### 构建卡住无输出

```bash
EDEN_MONO_IS_STREAM=1 emo start
```

## pnpm patch

EMO V3 中使用 `pnpm patch` 必须通过 EMO 包装命令：

```bash
# 打补丁
emo rpm patch <package-name>

# 提交补丁
emo rpm patch-commit <folder-path>
```

折叠模式（`"infraDir": "infra"`）下 patches 目录固定在 `${infraDir}/patches`。

## SCM 构建失败但本地成功

模拟 SCM 环境：

```bash
emo clean    # 还原到 clone 后状态
emo scm      # 模拟 SCM 局部安装
```

---

## 原始文档（需要飞书文档查看 skill）

- FAQ 开发构建与测试：<https://emo.bytedance.net/faq/dev-build-test.md>
- FAQ 依赖管理：<https://emo.bytedance.net/faq/dependency-management.md>
- FAQ 项目搭建：<https://emo.bytedance.net/faq/project-init.md>
- FAQ NPM 发布：<https://emo.bytedance.net/faq/npm-publish.md>
- FAQ Small Tips：<https://emo.bytedance.net/faq/small-tips.md>
