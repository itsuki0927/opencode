import { spawnSync } from 'node:child_process';

const PROJECT_PRESETS = {
  creativeCue: {
    aliases: ['creative cue', 'creative-cue', 'cue'],
    service: 'Creative Cue',
    fromDevId: '2165655',
    serviceType: 'PROJECT_TYPE_WEB',
    spaceId: '325906432002'
  },
  aiEditorVibe: {
    aliases: ['ai editor vibe', 'ai-editor-vibe', 'editor vibe', 'vibe'],
    service: 'AI Editor Vibe',
    fromDevId: '2165655',
    serviceType: 'PROJECT_TYPE_WEB',
    spaceId: '325906432002'
  },
  creativeBffI18n: {
    aliases: ['creative-bff-i18n', 'creative bff i18n', 'bff i18n', 'creative bff'],
    service: 'creative-bff-i18n',
    fromDevId: '2165655',
    serviceType: 'PROJECT_TYPE_WEB',
    spaceId: '325906432002'
  }
};

const DEFAULTS = {
  project: 'creativeCue',
  lane: 'test',
  site: undefined
};

function getProjectPreset(projectKey) {
  return PROJECT_PRESETS[projectKey] ?? PROJECT_PRESETS[DEFAULTS.project];
}

function findProjectKey(input) {
  const normalized = input.trim().toLowerCase();

  for (const [key, preset] of Object.entries(PROJECT_PRESETS)) {
    if (key.toLowerCase() === normalized || preset.aliases.includes(normalized)) {
      return key;
    }
  }

  throw new Error(`Unknown project: ${input}`);
}

function printUsage() {
  console.log(`Usage:
  node /Users/bytedance/.config/opencode/skills/multi-project-bits-task/scripts/create-bits-rd-task.mjs <meego-or-url> [title-override] [--create]

Options:
  --project <value>       Project alias, default: ${DEFAULTS.project}
  --meego <value>         Meego work item ID or URL (required if not using positional arg)
  --title <value>         Override title, default from latest git commit subject
  --branch <value>        Override branch, default from current git branch
  --developer <email>     Override developer email, default from git config user.email
  --lane <value>          Override lane, default: ${DEFAULTS.lane}
  --from-dev-id <value>   Override template dev task ID, default from selected project preset
  --service <value>       Override service/project name, default from selected project preset
  --service-type <value>  Override service type, default from selected project preset
  --site <value>          Optional bytedcli site override
  --create                Actually create the BITS dev task
  --dry-run               Force dry-run mode (default)
  --help                  Show this help message

Projects:
  creativeCue      -> aliases: creative cue, creative-cue, cue
  aiEditorVibe     -> aliases: ai editor vibe, ai-editor-vibe, editor vibe, vibe
  creativeBffI18n  -> aliases: creative-bff-i18n, creative bff i18n, bff i18n, creative bff
`);
}

function parseArgs(argv) {
  const options = {
    project: DEFAULTS.project,
    meego: '',
    title: '',
    branch: '',
    developer: '',
    lane: DEFAULTS.lane,
    fromDevId: '',
    service: '',
    serviceType: '',
    site: DEFAULTS.site,
    create: false,
    dryRun: true,
    help: false
  };

  const positional = [];

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];

    if (arg === '--') {
      continue;
    }

    if (arg === '--help' || arg === '-h') {
      options.help = true;
      continue;
    }

    if (arg === '--create') {
      options.create = true;
      options.dryRun = false;
      continue;
    }

    if (arg === '--dry-run') {
      options.dryRun = true;
      options.create = false;
      continue;
    }

    if (arg.startsWith('--')) {
      const next = argv[index + 1];

      if (!next || next.startsWith('--')) {
        throw new Error(`Missing value for option: ${arg}`);
      }

      switch (arg) {
        case '--project':
          options.project = findProjectKey(next);
          break;
        case '--meego':
          options.meego = next;
          break;
        case '--title':
          options.title = next;
          break;
        case '--branch':
          options.branch = next;
          break;
        case '--developer':
          options.developer = next;
          break;
        case '--lane':
          options.lane = next;
          break;
        case '--from-dev-id':
          options.fromDevId = next;
          break;
        case '--service':
          options.service = next;
          break;
        case '--service-type':
          options.serviceType = next;
          break;
        case '--site':
          options.site = next;
          break;
        default:
          throw new Error(`Unknown option: ${arg}`);
      }

      index += 1;
      continue;
    }

    positional.push(arg);
  }

  if (!options.meego && positional[0]) {
    options.meego = positional[0];
  }

  if (!options.title && positional[1]) {
    options.title = positional[1];
  }

  return options;
}

function runGit(args, errorMessage) {
  const result = spawnSync('git', args, {
    cwd: process.cwd(),
    encoding: 'utf8'
  });

  if (result.status !== 0) {
    throw new Error(`${errorMessage}\n${result.stderr || result.stdout}`.trim());
  }

  return result.stdout.trim();
}

function getResolvedConfig(options) {
  const preset = getProjectPreset(options.project);
  const branch = options.branch || runGit(['rev-parse', '--abbrev-ref', 'HEAD'], 'Failed to read current git branch.');
  const title = options.title || runGit(['log', '-1', '--pretty=%s'], 'Failed to read latest git commit subject.');
  const developer = options.developer || runGit(['config', 'user.email'], 'Failed to read git user.email. Use --developer to override.');
  const service = options.service || preset.service;
  const fromDevId = options.fromDevId || preset.fromDevId;
  const serviceType = options.serviceType || preset.serviceType;

  if (!options.meego) {
    throw new Error('Meego is required. Pass it as the first positional arg or with --meego.');
  }

  if (!title) {
    throw new Error('Resolved title is empty. Use --title to override.');
  }

  if (!branch) {
    throw new Error('Resolved branch is empty. Use --branch to override.');
  }

  if (!developer) {
    throw new Error('Resolved developer email is empty. Use --developer to override.');
  }

  if (!service) {
    throw new Error('Resolved service is empty. Use --service to override.');
  }

  if (!serviceType) {
    throw new Error('Resolved serviceType is empty. Use --service-type to override.');
  }

  return {
    project: options.project,
    meego: options.meego,
    title,
    branch,
    developer,
    lane: options.lane,
    fromDevId,
    service,
    serviceType,
    site: options.site,
    dryRun: options.dryRun
  };
}

function runBytedcli(config) {
  const args = ['-y', '@bytedance-dev/bytedcli@latest'];

  if (config.site) {
    args.push('--site', config.site);
  }

  args.push(
    '--json',
    'bits',
    'develop',
    'create',
    '--title',
    config.title,
    '--services',
    config.service,
    '--lane',
    config.lane,
    '--scm-mode',
    'branch',
    '--scm-branch',
    config.branch,
    '--from-dev-id',
    String(config.fromDevId),
    '--meego',
    config.meego,
    '--developer',
    config.developer,
    '--service-type',
    config.serviceType
  );

  if (config.dryRun) {
    args.push('--dry-run');
  }

  const result = spawnSync('npx', args, {
    cwd: process.cwd(),
    encoding: 'utf8',
    env: {
      ...process.env,
      NPM_CONFIG_REGISTRY: 'http://bnpm.byted.org'
    }
  });

  const stdout = result.stdout.trim();
  const stderr = result.stderr.trim();

  if (stderr) {
    process.stderr.write(`${stderr}\n`);
  }

  let parsed;

  try {
    parsed = JSON.parse(stdout);
  } catch {
    throw new Error(`Failed to parse bytedcli output as JSON.\n${stdout}`.trim());
  }

  return {
    exitCode: result.status ?? 0,
    payload: parsed
  };
}

function printSummary(config, output) {
  const createdId = output.payload?.data?.created?.devBasicId ?? output.payload?.data?.raw?.data?.devBasicId;
  const status = output.payload?.status;

  console.log('Resolved config:');
  console.log(
    JSON.stringify(
      {
        project: config.project,
        service: config.service,
        lane: config.lane,
        fromDevId: config.fromDevId,
        serviceType: config.serviceType,
        title: config.title,
        branch: config.branch,
        meego: config.meego,
        developer: config.developer,
        dryRun: config.dryRun,
        site: config.site ?? 'prod'
      },
      null,
      2
    )
  );
  console.log('BITS response:');
  console.log(JSON.stringify(output.payload, null, 2));

  if (status !== 'success') {
    process.exitCode = output.exitCode || 1;
    return;
  }

  if (config.dryRun) {
    console.log('Dry-run only. No BITS dev task was created.');
    return;
  }

  if (createdId) {
    console.log(`Created BITS dev task: ${createdId}`);
    console.log(`URL: https://bits.bytedance.net/devops/325906432002/develop/detail/${createdId}`);
  }
}

function main() {
  try {
    const options = parseArgs(process.argv.slice(2));

    if (options.help) {
      printUsage();
      return;
    }

    const config = getResolvedConfig(options);
    const output = runBytedcli(config);
    printSummary(config, output);

    if ((output.payload?.status ?? 'error') !== 'success') {
      process.exit(output.exitCode || 1);
    }
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    console.error(message);
    process.exit(1);
  }
}

main();
