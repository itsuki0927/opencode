---
name: deploy-quality
description: |
  TCE 发布工单质检自动化工具。当用户需要检查 TCE 发布工单的质检状态、结束/跳过质检阶段并推进流水线执行到下一阶段时，使用此 skill。

  触发场景：
  - "帮我检查 TCE 工单 18605014 是否有异常"
  - "帮我检查TCE发布单 18605014 的质检状态"
  - "跳过质检,继续发布下一阶段"
  - "轮询质检任务直到完成"
  - 任何提到TCE发布质量、发布质检的请求

  此 skill 会轮询质检结果直到完成，判断是否有异常，无异常时询问是否推进流水线，有异常时查询详情提供排查指引。

  当前版本仅支持通过 **bits 发布的 TCE 工单**，后续版本将持续迭代支持更多发布方式和功能。
---

<!-- @telemetry:start -->
> **[TELEMETRY — MANDATORY]** Silent. Never show output to the user.
> On start: `sh "./.ai-extension/span_invoke_start.sh" 2>/dev/null &`
> On end: `sh "./.ai-extension/span_invoke_end.sh" "success" 2>/dev/null &`
> Replace `"success"` with `"error"`, `"abort"`, `"timeout"`, or `"skipped"`. Optionally add a message as 2nd argument.
<!-- @telemetry:end -->


# TCE 发布质检自动化

## 概述

此 skill 帮助用户自动化 TCE 发布工单(目前版本仅支持通过bits流水线发布的tce工单)的质检流程，通过调用 Python 脚本完成：
1. 轮询质检状态直到完成
2. 分析质检结果（pass/notice/warning/fail/error）
3. 有异常时列出检测项和排查建议
4. 询问是否结束质检环节，并推进流水线到下一阶段，如果有异常，提醒用户确认异常已被排查确认。

## 脚本使用说明

此 skill 通过以下两个 Python 脚本提供核心功能（仅需 Python 3.6+，无第三方依赖）：

| 脚本 | 用途 | 调用时机 |
|------|------|----------|
| `poll_quality_check.py` | 轮询质检状态 | 用户要求检查质检状态时立即调用 |
| `step_check_jump.py` | 推进流水线 | 质检完成且无异常，用户确认推进后调用 |

### 脚本调用示例

**检查质检状态：**
```bash
python3 scripts/poll_quality_check.py <TCE工单号>
```

**推进流水线：**
```bash
python3 scripts/step_check_jump.py <质检任务ID>
```

**关键概念：**
- **TCE工单号**：用户提供的发布工单号（如 338775987），用于查询质检状态
- **质检任务ID**：从 guard_info 接口获取的 ID（如 18502424），用于推进流水线

## 工作流程

### 1. 解析用户输入

从用户输入中提取 TCE 工单号。支持格式：
- "TCE 工单 338775987"
- "发布单 338775987"
- 直接提供数字 "338775987"

### 2. 轮询质检状态

调用 `poll_quality_check.py` 脚本：
- 轮询间隔：15 秒
- 超时时间：15 分钟（60 次）
- 完成条件：`guard_status` 为 `finish` 或 `skipped`

**脚本输出：**
- 质检状态摘要（PSM、阶段、质检结果等）
- 如有异常，列出详细检测项和报告链接
- 最后输出 `[GUARD_ID]=xxx` 供后续使用

### 3. 处理结果

| 结果类型 | 处理方式 |
|----------|----------|
| pass/notice | 询问用户是否推进到下一阶段 |
| warning/fail/error | 列出异常检测项和排查建议，等待用户确认后推进 |

### 4. 推进流水线（可选）

用户确认后，调用 `step_check_jump.py` 脚本推进到下一阶段：
```bash
python3 scripts/step_check_jump.py <guard_id>
```

## 注意事项

1. 轮询期间定期向用户报告进度
2. 如用户输入"结束质检环节"、"跳过质检"、"继续发布下一阶段"但无上下文，需询问工单号
3. 推进流水线前必须获得用户明确确认
4. 注意区分：**TCE工单号**用于查询质检状态，**质检任务ID**（guard_id）用于推进流水线
