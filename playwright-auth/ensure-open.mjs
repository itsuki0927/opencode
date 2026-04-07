import { spawn } from 'node:child_process';
import process from 'node:process';

const DEFAULT_TARGET_URL = 'https://ads.tiktok.com/creative/creativestudio/create';

function getTargetUrl() {
  const cliTargetUrl = process.argv[2];
  const targetUrl = cliTargetUrl ?? process.env.TIKTOK_ADS_TARGET_URL ?? DEFAULT_TARGET_URL;
  const parsedUrl = new URL(targetUrl);

  if (parsedUrl.hostname !== 'ads.tiktok.com' || !parsedUrl.pathname.startsWith('/creative/')) {
    throw new Error(`Target URL must stay under https://ads.tiktok.com/creative/... Received: ${targetUrl}`);
  }

  return parsedUrl.toString();
}

function runNodeScript(scriptPath, targetUrl) {
  return new Promise((resolve, reject) => {
    const child = spawn(process.execPath, [scriptPath], {
      cwd: process.cwd(),
      env: {
        ...process.env,
        TIKTOK_ADS_TARGET_URL: targetUrl,
      },
      stdio: 'inherit',
    });

    child.on('error', reject);
    child.on('exit', (code) => {
      if (code === 0) {
        resolve();
        return;
      }

      reject(new Error(`${scriptPath} exited with code ${code ?? 'unknown'}`));
    });
  });
}

async function main() {
  const targetUrl = getTargetUrl();

  try {
    await runNodeScript('playwright-auth/check-auth.mjs', targetUrl);
    console.log('TikTok Ads auth is valid. Opening target page...');
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    console.log(`TikTok Ads auth check failed: ${message}`);
    console.log('Refreshing TikTok Ads auth before opening the target page...');
    await runNodeScript('playwright-auth/save-auth.mjs', targetUrl);
  }

  await runNodeScript('playwright-auth/open-create-page.mjs', targetUrl);
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : error);
  process.exitCode = 1;
});
