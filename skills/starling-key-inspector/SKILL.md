---
name: starling-key-inspector
description: Use this tool to query Starling localization keys by key text and return source text, per-language translation status, and publish status in structured JSON for agent workflows.
license: Proprietary.
---

# Starling Key Inspector

## Overview

The `starling-key-inspector` is a specialized CLI tool designed to query the Starling localization platform. It retrieves translation status, source text, and localized content across multiple languages.

**🤖 FOR AGENTS:** You **MUST** use the `--json` flag in your function calls to receive structured data. Do not parse the default human-readable table.

## Execution

Always execute the script using `bash` to ensure compatibility and avoid permission issues:

```bash
bash /path/to/starling-key-inspector/run <key_text> [options]
```

## Configuration & Discovery Logic

The tool automatically resolves **Credentials** and **Project Context** using the following priority order:

### 1. Authentication (AK/SK)
1. **CLI Arguments**: `--access-key` and `--secret-key`
2. **Local Project Config**: `starling.config.js` (if `accessKey`/`secretKey` are present)
3. **Environment Variables**: `STARLING_ACCESS_KEY` and `STARLING_SECRET_KEY`
4. **Global Config**: `~/.neeko-starling-config.json` (Automatically updated after successful queries)

### 2. Project Context (Project/Namespace ID)
1. **CLI Arguments**: `--project-id` and `--namespace-id`
2. **Local Project Config**: `starling.config.js` or `starling.config.cjs` in the current or parent directories.
3. **Global Config**: `~/.neeko-starling-config.json` (Automatically updated after successful queries)
4. **Auto-Discovery**: If no context is found, the tool searches for the key across **all authorized projects**.
    - **Batch Query Note**: When querying multiple keys (e.g., `key1,key2`), the tool uses the **first key** (`key1`) to perform the search across all accessible projects. Once the project context is found, it queries all keys within that project.

## Usage Examples

### 🤖 Agent Usage (JSON)
**Preferred method for AI agents.**

```bash
bash /path/to/starling-key-inspector/run <key_text> --json
```

### 👤 Human Usage (Interactive)
Standard output with formatted tables.

```bash
bash /path/to/starling-key-inspector/run <key_text>
```

### ⚙️ One-Time Setup (Recommended)
You can manually save your AK/SK locally, or simply run a query once with credentials provided. The tool will automatically cache them for future use.

```bash
bash /path/to/starling-key-inspector/run <any_key> \
  --access-key=<your_ak> \
  --secret-key=<your_sk>
```

## Parameters

| Parameter        | Type         | Description                                                                                                                  |
| ---------------- | ------------ | ---------------------------------------------------------------------------------------------------------------------------- |
| `key_text`       | **Required** | The localization key to query (e.g., `i_have_apples`). Support batch query with comma-separated keys (e.g., `key1,key2`).    |
| `--json`         | Flag         | **Required for Agents.** Outputs single-line JSON.                                                                           |
| `--save`         | Flag         | (Optional) Explicitly save provided Credentials and Project IDs to global config. Note: The tool also auto-saves on success. |
| `--project-id`   | Option       | Override Project ID.                                                                                                         |
| `--namespace-id` | Option       | Override Namespace ID.                                                                                                       |
| `--access-key`   | Option       | Starling Access Key.                                                                                                         |
| `--secret-key`   | Option       | Starling Secret Key.                                                                                                         |

## JSON Output Structure

### Success Response (Single Key Detail)

```json
{
  "key": "string",
  "id": number,
  "projectId": number,
  "namespaceId": number,
  "sourceText": "string",
  "sourceLang": "string",
  "updatedAt": "string",
  "translations": [
    {
      "lang": "string",
      "status": "string",
      "statusCode": number,
      "content": "string"
    }
  ]
}
```

### Error Response: Multiple Keys Found (Ambiguity)

If the key exists in multiple projects/namespaces, the tool returns an error with a list of candidates.

**🤖 AGENT ACTION:** When receiving this error, you MUST present the `candidates` list to the user and ask them to specify which project/namespace they want to query. Then, re-run the tool with the chosen `--project-id` and `--namespace-id`.

```json
{
  "error": "Multiple keys found",
  "code": "MULTIPLE_KEYS_FOUND",
  "candidates": [
    {
      "projectId": 123,
      "projectName": "Project A",
      "namespaceId": 456,
      "namespace": "Namespace X"
    },
    {
      "projectId": 789,
      "projectName": "Project B",
      "namespaceId": 101,
      "namespace": "Namespace Y"
    }
  ]
}
```