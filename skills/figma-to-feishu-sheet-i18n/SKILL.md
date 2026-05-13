---
name: figma-to-feishu-sheet-i18n
description: Read copy from Figma, generate semantic i18n-style keys, capture nearest-container screenshots, and write the result into a Feishu spreadsheet with a completion notification. Use this whenever the user wants to export Figma text to 飞书电子表格, generate i18n keys from a design, attach usage screenshots for copy, or organize design copy into a spreadsheet even if they do not explicitly mention this skill by name.
compatibility: Requires Figma design tools plus feishu-cli access for spreadsheet, media upload, and message sending.
allowed-tools: Figma design tools, Bash, Read, Write
---

# Figma To Feishu Sheet I18n

Turn Figma copy into a Feishu spreadsheet with semantic keys and usage screenshots.

## What This Skill Produces

Create a Feishu spreadsheet using this layout:

1. row 1: `namespace: <value>`
2. row 2 headers: `keys`, `screenshots`, `tag`, `length limit`, `Context`, `Source`

Default field policy:

- `keys`: required
- `screenshots`: required when possible; prefer sheet-anchored images and do not write placeholder text into the cell
- `tag`: leave blank unless the user explicitly asks
- `length limit`: leave blank unless the user explicitly asks
- `Context`: required
- `Source`: required and should contain the original copy text

## Default Behavior

- Output target: new Feishu spreadsheet in the default location
- Key style: `page_module_item`
- Screenshot style: nearest usable container screenshot
- Notification target: `liusenlin.0927@bytedance.com`
- Return the spreadsheet link in chat even if notification succeeds

## Inputs

Expected user input usually includes one of these:

- Figma URL
- Figma node ID
- A request to export copy from the currently selected Figma node

Optional inputs:

- custom spreadsheet title
- narrower scope such as a single page, modal, or component subtree
- highlighted screenshots that mark the source copy inside each usage screenshot

## Workflow

### 1. Read Figma structure

Use `figma_get_design_context` on the target node or page.

You need enough structure to identify:

- visible text nodes
- ancestor chain for each text node
- node names, types, and bounds
- absolute bounds for each text node and selected screenshot node when highlighted screenshots are requested
- top frame or page name

If the selected node is too narrow and misses surrounding context, move one level up and read again.

### 2. Extract copy candidates

Collect rows for user-facing copy only.

Include:

- titles
- subtitles
- labels
- placeholder text
- button text
- helper text
- empty state copy
- descriptions

Skip when practical:

- empty strings
- whitespace-only text
- obvious measurement tokens
- raw icon labels or engineering-only layer markers
- duplicate invisible text layers

### 3. Build page, module, and role

For each text candidate:

- `page`: infer from the top frame or page name
- `module`: infer from the nearest meaningful container around the text
- `role`: infer from node name and copy shape

Use the stable context format:

`page=<page>; module=<module>; role=<role>; text=<source_text>`

If exact semantics are unclear, prefer a plain but readable label over a clever guess.

### 4. Select screenshot node

The goal is not a tight crop around the text. The screenshot should explain where the copy is used.

Follow the rules in `references/screenshot_selection.md`.

In short:

- start from the text node's ancestors
- prefer the nearest usable container
- reject tiny nodes that do not show context
- reject very large nodes that become whole-page screenshots unless there is no better fallback

Use `scripts/select_screenshot_node.py` if you already have extracted ancestor metadata in JSON form.

### 5. Generate keys

Follow the rules in `references/key_rules.md`.

Use `scripts/generate_semantic_keys.py` or `scripts/build_sheet_rows.py` if you already converted the extracted text into JSON rows.

Key rules:

- format: `page_module_item`
- semantic names only
- lowercase snake case
- avoid weak names like `text_1`, `label_2`, `copy`, `content`

### 6. Capture screenshots

For each selected screenshot node, call `figma_get_screenshot` with that node ID.

Persist each screenshot to a local file and write its absolute path into the row's `screenshot_path`. A row with `screenshot_node_id` but an empty `screenshot_path` is incomplete and must not be treated as screenshot-ready.

Use a stable path pattern so later Feishu upload commands can find the files:

```text
/tmp/figma-to-feishu-sheet-i18n/<sheet_slug>/<row_index>_<screenshot_node_id>.png
```

Before creating or finalizing the sheet, validate that at least one exported row has a non-empty, existing `screenshot_path` when screenshot nodes were selected. If all `screenshot_path` values are empty, stop and fix screenshot capture; do not create a sheet and report screenshots as successful.

If a row fails because the selected node is invalid or unreadable:

1. retry with the next ancestor
2. if needed, fall back to the page or top frame
3. if all screenshot attempts fail, leave the screenshot cell empty and continue

If highlighted screenshots are requested:

1. preserve `text_bounds` from the text node's `absoluteBoundingBox`
2. preserve `screenshot_bounds` from the selected screenshot node's `absoluteBoundingBox`
3. run `scripts/highlight_screenshot_text.py` after screenshot capture
4. upload the highlighted output path, not the original screenshot path

Do not recreate the Figma UI in HTML or estimate red-box coordinates manually. Manual coordinates look acceptable for short labels near the container origin but drift for lower or multiline text because line-height, icon spacing, and screenshot scale are not tied to Figma geometry. Always derive highlight rectangles from Figma bounds and map them into PNG pixels.

### 7. Create Feishu spreadsheet

Use `feishu-cli` commands through Bash.

Before creating or updating a spreadsheet, run a lightweight auth/permission preflight:

```bash
feishu-cli auth status --verify -o json
feishu-cli sheet create --help
```

If any sheet, media, image, message, or permission command returns `缺少 app_id 或 app_secret 配置`, stop and report that App Token configuration is missing. User OAuth cannot fix permission-management APIs; configure `app_id` and `app_secret` in `~/.feishu-cli/config.yaml` or the supported environment variables, then retry.

If `~/.feishu-cli/config.yaml` exists but the command still reports missing `app_id` or `app_secret`, retry once with an explicit config path:

```bash
feishu-cli --config "$HOME/.feishu-cli/config.yaml" <command>
```

Use the explicit `--config` form for all follow-up sheet, media, image, permission, and notification commands in that run.

Recommended sequence:

```bash
feishu-cli sheet create --title "Figma Copy Export - YYYY-MM-DD"
feishu-cli sheet write <sheet_token> "A1:F<N>" --sheet-id <sheet_id> --data '<json matrix>'
```

Write namespace and headers before the data rows. Data starts from row 3.

Then place screenshots one row at a time in column `B`. The current `feishu-cli` supports floating sheet images via `sheet image add`; always anchor each image to its exact data row with `--range "B{row}:B{row}"` and keep the cell text empty.

Read `references/output_schema.md` for exact column order and command sequence.

### 8. Upload screenshots and place images

For each screenshot file:

1. calculate display dimensions with `scripts/prepare_sheet_image.py` so the image keeps its original aspect ratio
2. upload image to Feishu with sheet image semantics to obtain an image token
3. place image into the matching `screenshots` cell with `feishu-cli sheet image add`
4. verify placement with `feishu-cli sheet image list <spreadsheet_token> <sheet_id>` before reporting success

Use data row mapping exactly:

- first data row is spreadsheet row `3`
- row index `i` in the exported rows maps to spreadsheet row `i + 3`
- screenshot range is always `<sheet_id>!B{i + 3}:B{i + 3}` for `sheet image add`

Example:

```bash
python3 skills/figma-to-feishu-sheet-i18n/scripts/prepare_sheet_image.py screenshot.png 320 180
feishu-cli media upload screenshot.png --parent-type sheet_image --parent-node <spreadsheet_token> -o json
feishu-cli sheet image add <spreadsheet_token> <sheet_id> \
  --token <image_token> \
  --range "<sheet_id>!B3:B3" \
  --width <computed_width> \
  --height <computed_height>
feishu-cli sheet image list <spreadsheet_token> <sheet_id> -o json
```

Never reuse `<sheet_id>!B3:B3` for later rows. Never pass independent fixed width and height values that change the screenshot aspect ratio.

For the V3 floating image API, the range must include the sheet id prefix, for example `8a9003!B7:B7`. A bare `B7:B7` range can return `Wrong Sheet Id` even when `<sheet_id>` is passed as the positional argument.

Do not upload sheet screenshots as `docx_image`; those tokens are for document blocks and can make `sheet image add` silently produce no visible sheet images. If `media upload --parent-type sheet_image` fails, stop screenshot placement and report the failure instead of returning a sheet as fully successful.

After all image inserts, `sheet image list` must return at least the number of successful screenshot rows. If the list is empty, treat the export as screenshot placement failed and retry with the exact row ranges before notifying the user.

`scripts/build_sheet_image_commands.py` intentionally fails when rows contain `screenshot_node_id` but empty `screenshot_path`. This is a guardrail: it means screenshots were selected but never captured to local files, so there is nothing to upload.

If batch image placement is flaky, slow down and place them serially.

### 9. Send completion notification

Always try to send a Feishu message after sheet creation.

Use:

- `receive_id_type=email`
- `receive_id=liusenlin.0927@bytedance.com`

Include:

- spreadsheet title
- number of exported rows
- spreadsheet link

If the message fails, still return the link in chat.

### 10. Share sheet access

After creating the spreadsheet, grant access to the notification target so the user can open the result:

```bash
feishu-cli perm add <spreadsheet_token> \
  --doc-type sheet \
  --member-type email \
  --member-id liusenlin.0927@bytedance.com \
  --perm edit \
  --notification
```

If default config loading fails, use:

```bash
feishu-cli --config "$HOME/.feishu-cli/config.yaml" perm add <spreadsheet_token> \
  --doc-type sheet \
  --member-type email \
  --member-id liusenlin.0927@bytedance.com \
  --perm full_access \
  --notification
```

Prefer `full_access` for the configured recipient so they can view, edit, share, and repair the generated sheet. If the recipient only needs collaboration access, `edit` is acceptable.

If permission grant fails with `Permission denied` or missing app credentials, return the spreadsheet link but clearly mark it as not accessible yet. Do not claim the export is complete until access is granted or the user is told exactly which permission step failed.

## Output Contract

At the end, provide:

1. the Feishu spreadsheet link
2. how many rows were exported
3. whether screenshots were fully successful or partially missing
4. whether the Feishu notification was sent successfully
5. whether sheet access was granted successfully
6. which namespace value was used

## Helper Files

- `references/key_rules.md`: naming rules and examples
- `references/screenshot_selection.md`: nearest-container screenshot policy
- `references/output_schema.md`: sheet columns and Feishu write steps
- `scripts/generate_semantic_keys.py`: deterministic key generation from row JSON
- `scripts/select_screenshot_node.py`: deterministic container selection from ancestor JSON
- `scripts/build_sheet_rows.py`: combine extracted rows into final spreadsheet rows
- `scripts/highlight_screenshot_text.py`: draw copy highlight boxes from Figma `text_bounds` and `screenshot_bounds`
- `scripts/prepare_sheet_image.py`: calculate aspect-ratio-safe display dimensions for sheet images
- `scripts/build_sheet_image_commands.py`: generate row-safe upload/add/list commands for screenshot placement

## Failure Handling

- Prefer partial success over total failure.
- If screenshot placement fails, keep the spreadsheet and return the text rows.
- If spreadsheet permission grant fails, keep the spreadsheet and report the exact permission command that failed.
- If message send fails, do not retry indefinitely.
- If Figma extraction is noisy, ask one short question only when the scope is genuinely ambiguous.

## Example User Requests

- “把这个 Figma 页面里的文案整理到飞书表格，顺便生成 key 和截图。”
- “帮我从设计稿生成 i18n keys，放飞书 sheet，截图也带上。”
- “把登录页文案导出来，key 用 page_module_item，飞书通知我。”
