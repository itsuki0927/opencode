---
name: bytedance-bits
description: "Operate BITS DevOps platform via bytedcli: create dev tasks, run pipelines, update lanes, bind branches, and manage releases."
---

# bytedcli BITS

## When to use

- 创建研发任务（支持多项目多分支）
- 运行自测流水线
- 更新泳道配置
- 绑定代码分支
- 查询发布工作流
- 创建发布工单

## 前置条件

- 使用通用调用方式：`references/invocation.md`

> 示例省略 invocation 前缀。

## Quick start

### 创建研发任务

```bash
# 方式1: 使用 --services（向后兼容，单分支）
bytedcli bits develop create \
  --title "修复登录问题" \
  --services example.service.api \
  --lane test \
  --scm-mode branch \
  --scm-branch fix/login \
  --from-dev-id 12345 \
  --qa "qa@bytedance.com" \
  --meego "https://meego.feishu.cn/xxx/issue/detail/123" \
  --var "custom_var_key=自定义变量" \
  --developer "dev@bytedance.com" \
  --dry-run

# 方式2: 使用 --change（多项目多分支）
bytedcli bits develop create \
  --title "分享按钮修复" \
  --change "service=DevSRE|aily/nexus,branch=fix/share-button" \
  --change "service=DevSRE|aily/sandbox,branch=fix/share-align" \
  --lane test \
  --from-dev-id 12345 \
  --qa "qa@bytedance.com" \
  --meego "https://meego.feishu.cn/xxx/issue/detail/123" \
  --var "custom_var_key=自定义变量" \
  --developer "dev@bytedance.com" \
  --dry-run
```

### 运行自测流水线

```bash
bytedcli bits develop quick-run \
  --dev-id 2143012 \
  --stage DevDevelopStage \
  --task DevDevelopStageSelfTestTask \
  --control-planes CONTROL_PLANE_CN \
  --wait \
  --wait-timeout-sec 600
```

### 更新泳道

```bash
bytedcli bits develop update-lane \
  --dev-id 2143012 \
  --lane new_lane \
  --idcs lf,lq \
  --dry-run
```

### 绑定分支

```bash
bytedcli bits develop bind-branch \
  --dev-id 2143012 \
  --branch codex/feature \
  --git-repo stone/coze-coding \
  --services example.service.api \
  --dry-run
```

### 发布相关

```bash
# 查询发布工作流
bytedcli bits release list-workflows \
  --workspace-id 150900021762 \
  --keyword "快速发布"

# 获取发布表单 schema
bytedcli bits release form-schema \
  --workspace-id 150900021762 \
  --workflow-id 162749140482

# 创建发布工单
bytedcli bits release create-ticket \
  --workspace-id 150900021762 \
  --workflow-id 162749140482 \
  --name "v1.0.0 发布" \
  --release-approvers "alice,bob" \
  --projects-json '[...]'
```

## Notes

- 需要结构化输出加 `--json`
- `--change` 格式：`service=<PSM>,branch=<sourceBranch>[,target=<targetBranch>]`
- `--var` 可重复，格式：`name=value`
- `--env-setting-map-json` 用于覆盖创建接口的 `envSettingMap` 参数
- `--dry-run` 只打印 payload 不实际创建

## References

- `references/invocation.md`
