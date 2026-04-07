---
description: 确保 TikTok Ads Creative 已登录并打开指定 creative 页面
argument-hint: [https://ads.tiktok.com/creative/...]
allowed-tools: Bash(node playwright-auth/ensure-open.mjs*)
---

对 TikTok Ads Creative Studio 页面执行统一入口流程。

如果用户没有传 URL，先提示他们提供完整的 TikTok Ads Creative 页面地址。

如果用户传了 URL，就执行：

!`node playwright-auth/ensure-open.mjs "$ARGUMENTS"`

然后基于命令输出，简短说明发生了什么：

- auth 已有效则说明已直接打开目标页
- auth 缺失或过期则说明已进入手动登录流程并在完成后回到原始目标页
- 最终浏览器会保持打开，供用户继续操作
