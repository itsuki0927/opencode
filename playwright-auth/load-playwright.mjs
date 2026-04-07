import { execSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import { createRequire } from 'node:module';
import path from 'node:path';

const require = createRequire(import.meta.url);

function loadLocalPlaywright() {
  return require('playwright');
}

function getGlobalPlaywrightEntry() {
  const globalRoot = execSync('npm root -g', {
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'ignore'],
  }).trim();

  const packagePath = path.join(globalRoot, 'playwright');
  if (!existsSync(packagePath)) {
    throw new Error(`Global playwright package was not found under ${packagePath}`);
  }

  return packagePath;
}

function loadGlobalPlaywright() {
  return require(getGlobalPlaywrightEntry());
}

export function loadPlaywright() {
  try {
    return loadLocalPlaywright();
  } catch (localError) {
    try {
      return loadGlobalPlaywright();
    } catch (globalError) {
      const localMessage = localError instanceof Error ? localError.message : String(localError);
      const globalMessage = globalError instanceof Error ? globalError.message : String(globalError);
      throw new Error(
        `Unable to load Playwright from local or global install. Local error: ${localMessage}. Global error: ${globalMessage}`,
      );
    }
  }
}
