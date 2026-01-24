---
description: AI 辅助智能提交 - 运行 xcommit 并自动修复 TypeScript/ESLint 错误
---

加载 `commit-autofix` Skill，然后执行以下工作流：

1. 运行 `xcommit` 命令
2. 如果成功，显示 commit summary
3. 如果失败，将错误输出喂给 AI 进行修复
4. 修复后重试（最多 2 次）
5. 最后输出执行 Summary

开始执行...
