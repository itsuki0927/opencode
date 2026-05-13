---
name: bytedance-safe
description: Content moderation platform operations via bytedcli. Router skill for safe domain sub-skills.
---

# Safe Domain

Content moderation platform commands for querying features, entities, datasources, tenants, packages, collections, and more.

## Authentication

Before using any safe command, authenticate first:

```bash
# SSO-based login (requires prior `bytedcli auth login --session`)
bytedcli safe login

# Or paste cookie directly
bytedcli safe login --cookie "session=xxx"

# Or set environment variable
export SAFE_COOKIE="your_cookie_here"
```

## Configuration

Manage tenant, business, and other Safe settings:

```bash
bytedcli safe config get
bytedcli safe config get --key tenant
bytedcli safe config set --key tenant --value sample_tenant
bytedcli safe config clear --key tenant
```

## Sub-Domain Skills

| Sub-Domain | Skill                 | Description                                                                        |
| ---------- | --------------------- | ---------------------------------------------------------------------------------- |
| puzzle     | bytedance-safe-puzzle | Feature platform — features, entities, datasources, tenants, packages, collections |

## Quick Commands

```bash
# Features
bytedcli safe puzzle feature list
bytedcli safe puzzle feature get --id <id>
bytedcli safe puzzle feature test --id <id> --entity-params <json>
bytedcli safe puzzle feature update-rule-conf --id <id> --content data.json
bytedcli safe puzzle feature similar-search --keyword <meaning>

# Entities
bytedcli safe puzzle entity list
bytedcli safe puzzle entity get --id <id>

# Datasources
bytedcli safe puzzle datasource list --type redis --query demo
bytedcli safe puzzle ds get --id <id>

# Tenants
bytedcli safe puzzle tenant list
bytedcli safe puzzle tenant list --all

# Packages
bytedcli safe puzzle pkg list --keyword demo --exact-match
bytedcli safe puzzle pkg get --id <id>
bytedcli safe puzzle pkg list-features --id <id>

# Collections
bytedcli safe puzzle collection list --keyword demo --related-to-me false
bytedcli safe puzzle collection get --id <id>
bytedcli safe puzzle collection list-features --id <id>

# Datasource
bytedcli safe puzzle datasource list
bytedcli safe puzzle datasource create --type rpc --psm <psm> --method <method> --name <name>
bytedcli safe puzzle datasource similar-search --keyword <meaning>

# Tickets
bytedcli safe puzzle ticket list
bytedcli safe puzzle ticket create --id <id>
```

## Common Options

- `--tenant <tenant>` — Tenant for API requests. All puzzle sub-commands support this option. Priority: `--tenant` > `SAFE_TENANT` env > config > default `ecology`.
  - Config: `bytedcli safe config set --key tenant --value <tenant>`
- `--business <business>` — Business ID (default: default)
