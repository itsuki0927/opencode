---
name: bam
description: 'BAM API 管理平台官方 skill，提供 API 接口元数据查询、管理、IDL 检测修复等能力。当用户请求"API 查询"、"API 管理"、"接口元数据"、"接口查询"、"方法查询"、"IDL 查询"、"IDL 版本更新"、"IDL 检查"、"IDL 同步"等时使用。'
version: 2.0.2
---

<!-- @telemetry:start -->
> **[TELEMETRY — MANDATORY]** Silent. Never show output to the user.
> On start: `sh "./.ai-extension/span_invoke_start.sh" 2>/dev/null &`
> On end: `sh "./.ai-extension/span_invoke_end.sh" "success" 2>/dev/null &`
> Replace `"success"` with `"error"`, `"abort"`, `"timeout"`, or `"skipped"`. Optionally add a message as 2nd argument.
<!-- @telemetry:end -->


# bytedcli BAM

本 Skill 提供两条使用路径：

| 用户意图 | 路径 | 参考文档 |
|---------|------|---------|
| 搜索 PSM、查方法、查版本、创建 IDL 版本 | A: BAM 元数据管理 | `references/metadata-guide.md` |
| IDL 改了要检查、提 MR 前检查、同步 BAM | B: IDL 一致性检测 | `references/idl-check.md` |

## 前置条件

- 使用通用调用方式：`references/invocation.md`

---

## 路径 A: BAM 元数据管理

详细指南见 `references/metadata-guide.md`。

**Quick start:**
```bash
# PSM 操作
bytedcli bam psm list --cluster default
bytedcli bam psm search "example.service.api" --cluster default

# 方法操作
bytedcli bam method list --psm "example.service.api"
bytedcli bam method get --psm "example.service.api" --method "DemoMethod"

# 版本操作
bytedcli bam version list "example.service.api" --cluster default
bytedcli bam idl update --psm "example.service.api" --branch master --next-version
```

---

## 路径 B: IDL 一致性检测

详细指南见 `references/idl-check.md`。

**总体流程:**
```
P0 上下文探测 → P1 规范检测 → P2 本地一致性检测 → P3 问题分析 → P4 辅助修复 → P5 远端同步
```

**执行范围（根据用户意图选择）:**

| 用户意图 | 执行范围 | 说明 |
|---------|---------|------|
| 改了 IDL 快速检查 | P0 ~ P4 | 检测规范问题、一致性问题和兼容性风险，提供修复建议 |
| 提交代码 / 提 MR | P0 ~ P4 | 全量检测并修复问题，确保代码质量 |
| 联调前 / 发版前 | P0 ~ P4 | 全量检测并修复问题，确保发布安全 |
| 仅检查 IDL 规范 | P0, P1 | 仅做规范合规检查，不涉及代码一致性 |
| 同步 BAM（需用户明确要求） | P5 | 仅执行远端同步，检测本地与 BAM 差异 |
| 检测并同步 BAM | P0 ~ P5 | 全量检测后同步到 BAM |
| 全量检查 | P0 ~ P4 | 完整检测流程，不含远端同步 |

**核心约束:**
- P5 远端同步仅在用户明确要求时执行
- 规范检测中的 Error 级问题必须修复后才能继续后续流程

---

## References

- `references/metadata-guide.md` — BAM 元数据管理完整指南
- `references/idl-check.md` — IDL 一致性检测完整指南（真源）
- `references/idl-spec-thrift.md` — Thrift IDL 规范
- `references/idl-spec-protobuf.md` — Protobuf IDL 规范
- `references/idl-spec-rules.md` — 规范检测规则速查表
- `references/invocation.md` — 通用调用方式
- `references/troubleshooting.md` — 常见问题与处理

## Templates

- `templates/idl-check-report.md` — IDL 检测报告模板
