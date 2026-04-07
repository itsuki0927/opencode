---
name: tiktok-ads-save-auth
description: Ensure TikTok Ads Creative Studio has a usable login session before browser automation. Use when the user asks to open, access, test, inspect, or automate any `ads.tiktok.com/creative...` page, Symphony Creative Studio, or TikTok Ads Creative Studio workflow, and also before Playwright/browser navigation to those pages when login or captcha might block progress. Trigger this skill before browser actions on that domain unless you have already verified a valid saved auth state in this session.
allowed-tools: Bash(node playwright-auth/ensure-open.mjs*), Bash(node playwright-auth/check-auth.mjs), Bash(node playwright-auth/save-auth.mjs)
---

# TikTok Ads Creative Studio auth bootstrap

This skill makes TikTok Ads Creative Studio browser work reliable by routing everything through one unified entry.

## Use this flow

1. Prefer the single user-facing entry when you know the target page:

```bash
/tiktok-ads-open https://ads.tiktok.com/creative/...
```

2. The unified entry does all of this for you:

- checks whether the saved auth state is still valid for that exact target page
- if auth is missing or expired, launches the manual login flow
- after login succeeds, returns to the original target page
- opens the target page and leaves the browser open

3. Use the lower-level scripts only when you intentionally need a split flow.

4. For debugging or custom orchestration, you can still run the fast auth check yourself:

```bash
TIKTOK_ADS_TARGET_URL="https://ads.tiktok.com/creative/..." node playwright-auth/check-auth.mjs
```

5. If the check succeeds, report that the existing auth state is still valid and continue with the user's browser task.

6. If the check fails because the auth file is missing, expired, or redirects back to login, immediately run:

```bash
TIKTOK_ADS_TARGET_URL="https://ads.tiktok.com/creative/..." node playwright-auth/save-auth.mjs
```

7. Tell the user what to do in the browser:
   - manually sign in
   - solve captcha
   - accept consent dialogs
   - choose the right ad account
   - return to the terminal and press Enter

8. After `save-auth.mjs` finishes successfully, tell the user the TikTok Ads auth state has been refreshed and that the browser has already returned to the original target page.

## Important constraints

- Do not ask the user to paste passwords into chat.
- Do not try to bypass or automate captcha.
- Prefer refreshing the saved auth state over using a normal personal Chrome profile.
- If the check script reports valid auth, do not force a re-login.
- Prefer `/tiktok-ads-open <url>` as the default user-facing entry, and pass the real target page so the post-login page matches the original requested URL.

## Output expectations

When you use this skill, clearly say one of:

- `TikTok Ads auth is still valid; continuing without re-login.`
- `TikTok Ads auth is missing or expired; please complete the browser login flow now.`
- `TikTok Ads auth refresh completed; the browser has returned to the requested Creative page.`
