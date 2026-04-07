import { mkdir } from 'node:fs/promises';
import path from 'node:path';
import process, { stdout as output } from 'node:process';

import { loadPlaywright } from './load-playwright.mjs';

const AUTH_PATH = process.env.TIKTOK_ADS_AUTH_PATH ?? 'playwright-auth/.auth/tiktok-ads.json';
const DEFAULT_TARGET_URL = 'https://ads.tiktok.com/creative/creativestudio/create';
const LOGIN_WAIT_TIMEOUT_MS = 3 * 60 * 1000;
const LOGIN_POLL_INTERVAL_MS = 10 * 1000;

function getTargetUrl() {
  const targetUrl = process.env.TIKTOK_ADS_TARGET_URL ?? DEFAULT_TARGET_URL;
  const parsedUrl = new URL(targetUrl);

  if (parsedUrl.hostname !== 'ads.tiktok.com' || !parsedUrl.pathname.startsWith('/creative/')) {
    throw new Error(`TIKTOK_ADS_TARGET_URL must stay under https://ads.tiktok.com/creative/... Received: ${targetUrl}`);
  }

  return parsedUrl.toString();
}

function getLoginUrl(targetUrl) {
  return `https://ads.tiktok.com/i18n/login?redirect=${encodeURIComponent(targetUrl)}`;
}

function printManualLoginInstructions() {
  output.write('\nFinish the login flow in the browser window.\n');
  output.write('- Enter email/password\n');
  output.write('- Solve the captcha manually\n');
  output.write('- Accept any consent dialog\n');
  output.write('- Choose the correct account if TikTok Ads asks\n');
  output.write(`\nThis script will detect success automatically and check every ${LOGIN_POLL_INTERVAL_MS / 1000} seconds.\n`);
  output.write(`It will keep waiting for up to ${LOGIN_WAIT_TIMEOUT_MS / 60000} minutes before timing out.\n\n`);
}

async function waitForCreativeStudio(page) {
  const startTime = Date.now();

  while (Date.now() - startTime < LOGIN_WAIT_TIMEOUT_MS) {
    if (page.isClosed()) {
      throw new Error('TikTok Ads login browser page was closed before auth could be saved.');
    }

    try {
      await page.waitForURL('https://ads.tiktok.com/creative/**', {
        timeout: LOGIN_POLL_INTERVAL_MS,
        waitUntil: 'domcontentloaded',
      });
      await page.waitForTimeout(2_000);

      if (page.isClosed()) {
        throw new Error('TikTok Ads login browser page was closed before auth could be saved.');
      }

      await page.waitForLoadState('networkidle', { timeout: 30_000 }).catch(() => {});
      const currentUrl = page.url();

      if (currentUrl.includes('/login')) {
        continue;
      }

      if (!currentUrl.startsWith('https://ads.tiktok.com/creative/')) {
        continue;
      }

      return currentUrl;
    } catch {
      if (page.isClosed()) {
        throw new Error('TikTok Ads login browser page was closed before auth could be saved.');
      }

      const elapsedSeconds = Math.floor((Date.now() - startTime) / 1000);
      output.write(`Still waiting for Creative Studio login completion... (${elapsedSeconds}s elapsed, current URL: ${page.url()})\n`);
    }
  }

  throw new Error(`Timed out after ${LOGIN_WAIT_TIMEOUT_MS / 60000} minutes waiting for TikTok Ads Creative Studio login. Last URL: ${page.url()}`);
}

async function main() {
  const { chromium } = loadPlaywright();
  const targetUrl = getTargetUrl();
  const loginUrl = getLoginUrl(targetUrl);

  await mkdir(path.dirname(AUTH_PATH), { recursive: true });

  const browser = await chromium.launch({
    channel: 'chrome',
    headless: false,
    slowMo: 50,
  });

  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    await page.goto(loginUrl, { waitUntil: 'domcontentloaded' });
    printManualLoginInstructions();

    const finalUrl = await waitForCreativeStudio(page);

    if (!finalUrl.startsWith('https://ads.tiktok.com/creative/')) {
      throw new Error(`Login did not finish on a TikTok Ads creative page. Current URL: ${finalUrl}`);
    }

    await context.storageState({ path: AUTH_PATH });

    output.write(`\nSaved auth state to ${AUTH_PATH}\n`);
    output.write(`Returned page after login: ${finalUrl}\n`);
    output.write('You can now use open-create-page.mjs to verify the saved session.\n');
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : error);
  process.exitCode = 1;
});
