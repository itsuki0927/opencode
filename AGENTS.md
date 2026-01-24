# AGENTS.md - OpenCode Configuration Repository

## Repository Structure
This repository contains configuration, skills, and commands for OpenCode agentic workflows.
- `opencode.json`: Core configuration for providers, models, and MCP servers.
- `oh-my-opencode.json`: Agent-specific model assignments and global settings.
- `skills/`: Modular packages extending agent capabilities with specialized logic.
  - `{skill}/SKILL.md`: Required entry point with metadata and instructions.
  - `{skill}/scripts/`: Executable Python/Bash scripts for deterministic tasks.
  - `{skill}/references/`: Domain-specific documentation and schemas.
  - `{skill}/assets/`: Templates, images, and boilerplate files.
- `commands/`: Markdown files defining slash commands and their workflows.
- `.sisyphus/`: Internal state and notepads for the Sisyphus execution engine.

## Build/Lint/Test Commands
The repository does not use a global build system. Agents should use standalone tools.
- Running Python scripts: `python skills/{skill}/scripts/{script}.py [args]`
- Validating Python syntax: `python -m py_compile skills/{skill}/scripts/{script}.py`
- Linting/Formatting: Use standard LSP diagnostics via `lsp_diagnostics`.
- Git operations: Use `xcommit` for atomic commits with automatic error fixing.
- Manual verification: Execute scripts directly and inspect stdout/stderr.
- No global test framework: Test scripts individually using representative samples.

## Code Style Guidelines
### Python Scripts
Follow these patterns for consistency and reliability in agent-generated code.
- Imports: Order as standard library → third-party packages → local modules.
- Type hints: Required for all function signatures and class attributes.
- Docstrings: Use triple quotes (""") for modules, classes, and public functions.
- Naming: Use `snake_case` for files, functions, and variables; `PascalCase` for classes.
- Error handling: Use early returns and provide actionable, descriptive error messages.
- CLI structure: Check `sys.argv` length and print usage instructions if incorrect.
- Path handling: Always use `pathlib.Path` for cross-platform compatibility.
- Data structures: Prefer `dataclasses` for structured data containers.

### JavaScript (Limited Use)
- Syntax: Use ES6+ features (arrow functions, destructuring, template literals).
- Contexts: Primarily used for `html2pptx` logic or `p5.js` algorithmic art templates.

### Markdown (SKILL.md)
- Frontmatter: Must include `name` and `description` in YAML format.
- Description: Must be comprehensive as it serves as the primary triggering mechanism.
- Progressive disclosure: Keep `SKILL.md` lean; move details to `references/` files.
- Tone: Use imperative or infinitive form for instructions.

## Skill Development Guidelines
- Initialization: Use `python scripts/init_skill.py <name>` to create the structure.
- Determinism: Move repetitive or fragile logic into scripts instead of raw prompts.
- Context efficiency: Only include information that an AI agent cannot derive.
- Packaging: Run `python scripts/package_skill.py <path>` to validate and bundle.
- Validation: The packager checks frontmatter, directory structure, and references.
- Iteration: Refine skills based on performance in real-world tasks.

## Configuration Files
- `opencode.json`: Defines the `$schema`, active plugins, and provider model limits.
- `oh-my-opencode.json`: Maps agent roles (e.g., sisyphus, librarian) to specific models.
- `commands/*.md`: Defines slash commands using Markdown with YAML descriptions.

## Common Patterns
- JSON processing: Use `json.load()` and `json.dump()` with proper error handling.
- Path resolution: Use `Path(__file__).parent` to locate bundled resources.
- Actionable output: Scripts should print clear SUCCESS/FAILURE messages for agents.

## Important Notes
- No tests required: Focus on standalone reliability and manual verification.
- Context is a public good: Minimize token usage in instructions and references.
- Standalone scripts: Ensure scripts are self-contained or use relative imports.
- No emojis: Maintain a professional, concise tone without decorative elements.

## Detailed Python Style Examples
### Import Order
```python
import json
import sys
from pathlib import Path

import imageio.v3 as imageio
import numpy as np

from .utilities import XMLEditor
```

### Type Hints and Dataclasses
```python
@dataclass
class RectAndField:
    rect: list[float]
    rect_type: str
    field: dict
```

### CLI Script Structure
```python
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: check_bounding_boxes.py [fields.json]")
        sys.exit(1)
    with open(sys.argv[1]) as f:
        messages = get_bounding_box_messages(f)
```

## Detailed Skill Structure
### SKILL.md Frontmatter
```yaml
---
name: skill-name
description: Comprehensive description of what the skill does and when to use it.
---
```

### Directory Layout
- `scripts/`: `rotate_pdf.py`, `validate_schema.py`
- `references/`: `api_docs.md`, `schemas.json`
- `assets/`: `logo.png`, `template.docx`

## Progressive Disclosure Patterns
- **Pattern 1**: High-level guide in `SKILL.md` with links to `references/`.
- **Pattern 2**: Domain-specific organization (e.g., `references/aws.md`, `references/gcp.md`).
- **Pattern 3**: Conditional details (e.g., "For tracked changes, see REDLINING.md").

## Git Workflow Details
- Use `xcommit` for all commits.
- Ensure atomic changes per commit.
- Follow the repository's commit message style.

## JSON Configuration Reference
### opencode.json
- `plugin`: List of active plugins.
- `provider`: Model definitions and limits.
- `mcp`: Remote or local MCP server configurations.

### oh-my-opencode.json
- `agents`: Mapping of agent roles to specific models.
- `google_auth`: Boolean flag for Google authentication.

## Final Reminders
- Keep `SKILL.md` under 500 lines.
- Use `pathlib.Path` for all file operations.
- Test scripts by running them before packaging.
- Avoid redundant documentation files like `README.md` inside skills.
