# Merlin CLI Reference

Merlin commands cover five workflows:

- `job`: list job runs, resolve a job to trial ids, extract a submit-ready YAML from an existing job, then submit that YAML again
- `trial`: diagnose one trial or read one trial's local training log
- `logs`: read stdout/stderr log lines for trials under a Merlin job
- `tracking`: read projects, runs, metric names, scalar series, and job-to-tracking links
- `quota`: read groups and clusters through `merlin quota`

## Table of Contents

- [Environment selection](#environment-selection)
- [Site mapping commands](#site-mapping-commands)
- [Job](#job)
- [Trial](#trial)
- [Logs](#logs)
- [Tracking](#tracking)
- [Quota](#quota)
- [Authentication](#authentication)
- [JSON output](#json-output)

## Environment selection

- Use global `--site` and optional `--vregion` to choose the Merlin environment.
- Merlin supports these canonical sites: `cn`, `i18n-bd`, `i18n-tt`, `eu-ttp`, `us-ttp-bdee`, `us-ttp-usts`.
- Only `cn` and `i18n-bd` accept `--vregion seed`.
- Merlin does not support `--vdc`. Passing a non-empty `--vdc` returns an input error.
- `list-sites` defaults to `Site | VRegion | VDC | Remark | Origin | API Root`; `job list-sites` additionally prints `Job Core API Root`, `Job Trials API Root`, and `Job Trials Fallback API Root`.
- Unset `vregion` and `vdc` values are rendered as the literal string `null`.
- Bare job ids and direct trial ids use the current global Merlin environment. Full Merlin URLs use the URL host embedded in the input.

## Site mapping commands

```bash
bytedcli merlin job list-sites
bytedcli merlin trial list-sites
bytedcli merlin logs list-sites
bytedcli merlin tracking list-sites
bytedcli merlin quota list-sites
```

`API Root` is surface-specific:

- `job`: `${origin}/api/v1`; `job list-sites` also exposes `job_core_api_root`, `job_trials_api_root`, and `job_trials_fallback_api_root`
- `trial`: `${origin}/arnold/api/v3`
- `logs`: `${origin}/api/training/merlin_job/log/streamlog`
- `tracking`: `${origin}/open`
- `quota`: `${origin}/arnold/api/v3`

## Job

List job runs or resolve trial ids:

```bash
bytedcli merlin job list
bytedcli merlin job list --status running,failed --keyword proposal --page-size 50
bytedcli merlin job list --queued --page-size 50
bytedcli merlin job trials --job <job-id-or-url>
```

Extract submit-ready YAML from a Merlin job id or full job URL:

```bash
bytedcli merlin job extract --job <job-id-or-url>
bytedcli --site cn --vregion seed merlin job extract --job <job-run-id>
bytedcli merlin job extract --job "https://example.merlin.site/development/instance/jobs/<job-run-id>" --output ./trial.yaml
```

Submit a Merlin job from a local YAML file:

```bash
bytedcli merlin job submit --body-file ./trial.yaml
bytedcli --site i18n-bd --json merlin job submit --body-file ./trial.yaml
```

Notes:

- `job list` defaults to the current authenticated username and matches the web page's MINE semantics.
- Use `job list --queued` when checking where submitted jobs are queued. The web page's queued state can appear as job core `STARTED` plus `meta.arnoldTrialStatus=queued`, so filtering only `--status waiting,pending,running` can miss queued jobs.
- `job trials` first queries `/arnold/api/v3/trials/basic?custom_id=<job-id>` to enumerate Arnold trials attached to the Merlin job run.
- If that Arnold lookup returns no trials, `job trials` falls back to `/api/v1/job_run/get/<job-id>` and extracts non-empty, non-zero trial ids from the current job record.
- `job extract --job <job-run-id>` uses the current global Merlin environment.
- `job extract --job <full-url>` uses the URL host instead.
- `job submit` sends the YAML to the resolved job API Root and returns the new job URL.

## Trial

Diagnose a trial or read its local training log:

```bash
bytedcli merlin trial list-sites
bytedcli merlin trial diagnose --trial-id <trial-id>
bytedcli merlin trial local-log --trial-id <trial-id>
bytedcli merlin trial local-log --trial-id <trial-id> --stream stderr --tail 200
```

Notes:

- `trial diagnose` uses the Arnold-backed trial diagnose endpoint and is mainly useful for scheduling, quota, or queue-related diagnosis.
- When the backend has no active scheduling diagnosis for the trial, the response may only contain `DiagnosticCode: 0` with an empty `DiagnosticInfo` and null `QueueInfo`.
- `trial list-sites` currently shows the same Arnold root mapping family as `quota list-sites`.
- `trial local-log` uses Arnold `instances` + `locallog`, not Streamlog.
- `trial local-log --stream` only accepts `stdout` or `stderr`.

## Logs

Query stdout/stderr logs by job or by trial:

```bash
bytedcli merlin logs get --job <job-run-id>
bytedcli merlin logs get --job "https://example.merlin.site/development/instance/jobs/<job-run-id>?trialId=<trial-id>&tabState=log" --stream stderr --tail 50
bytedcli merlin logs get --trial-id <trial-id> --stream stderr --pod-name <kubernetes-pod-name> --tail 50
bytedcli merlin logs get --trial-id <trial-id> --stream both --all-instances --all
bytedcli --json merlin logs get --job <job-run-id> --role-name <role-name>
```

Key options:

- `--job <jobIdOrUrl>`
- `--trial-id <id>`
- `--stream <stdout|stderr|both>`
- `--tail <n>`
- `--all`
- `--role-name <name>`
- `--instance-id <id>`
- `--pod-name <name>`
- `--all-instances`

Notes:

- `--job` and `--trial-id` are mutually exclusive.
- `--instance-id` and `--all-instances` are mutually exclusive.
- When exact backend alignment matters, prefer `--pod-name`.
- `logs list-sites` shows the Streamlog API Root, not the job API Root.

## Tracking

List or read tracking projects:

```bash
bytedcli merlin tracking project list --keyword demo --limit 5
bytedcli merlin tracking project get --project-name ci
bytedcli merlin tracking project get --project-id <project-id>
```

List or read runs:

```bash
bytedcli merlin tracking run list --project-name ci --limit 10
bytedcli merlin tracking run get --project-name ci --run-id <run-id>
bytedcli merlin tracking run entity-names --project-name ci --run-id <run-id>
bytedcli merlin tracking run scalar list --project-name ci --run-id <run-id> --name train/loss,val/loss
```

Resolve tracking links from a Merlin job run id:

```bash
bytedcli merlin tracking job links --job-run-id <job-run-id>
```

Notes:

- `tracking run scalar list` reads scalar data from `${origin}/open/tracking`.
- Use `--project-id` or `--project-name` as the project selector, depending on the subcommand.
- `job links` is the fastest path when you only have a Merlin job run id.

## Quota

List visible group memberships:

```bash
bytedcli merlin quota group list
bytedcli merlin quota group list --approved-only
```

Read one group's cluster-level resources:

```bash
bytedcli merlin quota group resources --group-id 271
```

List clusters:

```bash
bytedcli merlin quota cluster list
```

Notes:

- `quota group list` returns membership rows.
- `group resources` expects `group.id`, not `group.name`.

## Authentication

- Merlin reuses `bytedcli auth login` state and the current ByteCloud JWT flow.
- In normal usage, set `--site` and optional `--vregion`; do not pass `--auth-site` unless you need to override the default auth environment explicitly.

## JSON output

- Prefer `bytedcli --json merlin ...` when another tool needs machine-readable output.
- Merlin JSON payloads now expose canonical environment fields: `site`, `vregion`, `vdc`, `origin`, and `api_root`.
