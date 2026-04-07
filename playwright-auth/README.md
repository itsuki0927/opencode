# TikTok Ads Playwright auth helpers

These two scripts split the flow into:

1. Manual login once, including captcha, then save `storageState`
2. Reuse that saved auth state to open the original TikTok Ads creative page directly
3. Or use one unified entry that ensures auth first, then opens any target creative page

## Setup

Install Playwright locally first, or make sure it is available as a global npm package:

```bash
npm install -D playwright
npx playwright install chromium
```

## 1) Save auth after manual login

```bash
node playwright-auth/save-auth.mjs
```

What happens:

- The browser opens the TikTok Ads login page directly
- You manually log in, solve captcha, accept consent, and choose the account
- The script auto-detects when you reach Creative Studio and saves auth without terminal input
- The script saves auth to `playwright-auth/.auth/tiktok-ads.json`
- If `TIKTOK_ADS_TARGET_URL` is provided, login redirects back to that original target page

## 2) Reuse saved auth

```bash
node playwright-auth/open-create-page.mjs
```

If the auth state is still valid, the browser opens the target create page without going back through login and stays open until you close the browser window.

## 3) Unified entry for any TikTok Ads creative page

```bash
node playwright-auth/ensure-open.mjs "https://ads.tiktok.com/creative/creativestudio/create"
```

If you are using the local command layer, prefer:

```bash
/tiktok-ads-open https://ads.tiktok.com/creative/creativestudio/create
```

What it does:

- checks whether the saved auth state is still valid for the target page
- if not, runs the manual login flow
- after login succeeds, returns to the original target page
- opens the target page and leaves the browser open for you

## Optional env override

Both scripts support a custom auth-state path:

```bash
TIKTOK_ADS_AUTH_PATH=/absolute/or/relative/path.json node playwright-auth/save-auth.mjs
```

They also support a custom target creative page:

```bash
TIKTOK_ADS_TARGET_URL="https://ads.tiktok.com/creative/creativestudio/create" node playwright-auth/save-auth.mjs
TIKTOK_ADS_TARGET_URL="https://ads.tiktok.com/creative/creativestudio/create" node playwright-auth/check-auth.mjs
TIKTOK_ADS_TARGET_URL="https://ads.tiktok.com/creative/creativestudio/create" node playwright-auth/open-create-page.mjs
node playwright-auth/ensure-open.mjs "https://ads.tiktok.com/creative/creativestudio/create"
```

## Notes

- Do not commit the auth file. `.gitignore` already excludes `playwright-auth/.auth/`.
- If TikTok Ads sends you back to login, re-run `save-auth.mjs`.
- The scripts do not store email or password in code.
- The scripts prefer your locally installed Google Chrome via Playwright `channel: 'chrome'`.
