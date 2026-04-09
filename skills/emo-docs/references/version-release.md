# 版本管理与发布

EMO 使用 Changeset 工作流管理版本和发布。流程：`add-changeset` → `version` → `publish`。

## 1. 添加 Changeset

```bash
# 交互式选择变更的包
emo add-changeset

# 指定版本级别和描述
emo add-changeset --type patch --summary "修复 xxx 问题"

# 自动选择所有 git diff 检测到的变更包
emo add-changeset --changed

# 初始化 changeset 配置（首次使用）
emo add-changeset --init
```

注意：要发布的包 `package.json` 中 `private` 不能为 `true`。

## 2. 版本更新

```bash
# 消耗 changeset 文件，更新 version 和 CHANGELOG.md
emo version

# 预览版本（不消耗 changeset，不更新 CHANGELOG）
emo version --preview

# 预发布版本（alpha/beta，更新 CHANGELOG 但保留 changeset）
emo version --prerelease alpha

# 仅更新指定包（不联动依赖者）
emo version --filter "@scope/lib" --independent

# 自动提交并推送
emo version --commit --push --git-tag
```

## 3. 发布

```bash
# 发布
emo publish

# 发布预览版
emo publish --preview
emo publish --preview canary  # 指定 tag

# 指定 npm tag
emo publish --tag beta

# 指定版本号
emo publish --specified-version 1.2.3

# 试运行
emo publish --dry-run

# 禁用 git tag
emo publish --no-git-tag

# 过滤 workspace
emo publish --filter "@scope/lib"
```

---

## 原始文档

- emo add-changeset：<https://emo.bytedance.net/cli/version-release/add-changeset.md>
- emo version：<https://emo.bytedance.net/cli/version-release/version.md>
- emo publish：<https://emo.bytedance.net/cli/version-release/publish.md>
- NPM 发布教程：<https://emo.bytedance.net/tutorial/internal-platform/bnpm-publish.md>
