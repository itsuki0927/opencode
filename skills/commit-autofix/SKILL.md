---
name: commit-autofix
description: |
  AI-assisted git commit with automatic error fixing.
  Triggers: /commit command, xcommit failures, TypeScript/ESLint errors.
  Focus: TypeScript (.ts) and TypeScriptReact (.tsx) and Css(.css/.scss/.less) files.
---

# Commit AutoFix

## Workflow

### Step 1: Execute xcommit

```bash
xcommit
```

捕获命令的 stdout 和 stderr。

### Step 2: Handle Result

**如果成功 (exit code 0)**:
进入 Step 4 输出 Summary。

**如果失败**:

1. 显示通知：
   ```
   ⚠️ 检测到错误，正在进行修复中...
   ```
2. 将完整错误输出直接交给 AI 分析
3. AI 读取相关文件并修复（重点关注 .ts/.tsx 文件）
4. 修复后 `git add` 修改的文件

### Step 3: Retry (最多 2 次)

重新执行 `xcommit`，重复 Step 2。

### Step 4: Output Summary

**成功时**:

```
✅ Commit 成功！

Summary:
- Commit: <hash>
- Message: <commit message>
- 修复的文件: <list> (如有)
```

**失败时**:

```
❌ Commit 失败

Summary:
- 尝试次数: 3
- 剩余错误:
  <error output>
- 建议: 请手动检查上述错误
```

### Step 5: Ask Push to Remote

**仅在 commit 成功后执行此步骤。**

询问用户是否要 push 到远程仓库：

```
🚀 是否要将此 commit push 到远程仓库？
```

**如果用户确认 push**:

1. 执行 `git push`
2. 显示 push 结果

**如果用户拒绝**:
结束工作流。

## Guardrails

- 最多重试 2 次（共 3 次尝试）
- 不修复单元测试失败
- 不使用 --no-verify
- 重点关注 TypeScript/TypeScriptReact 文件
- Push 操作需要用户明确确认
