# Figma To Feishu Sheet I18n Skill Design

## Goal

Create a reusable skill that reads copy from Figma, generates semantic `page_module_item` keys, captures a nearby usage screenshot for each string, writes the result into a Feishu spreadsheet, sends a Feishu notification, and returns the spreadsheet link in chat.

## User Decisions

- Output target: Feishu spreadsheet in default location
- Sheet layout follows provided localization template
- Screenshot style: nearest usable container screenshot
- Key style: `page_module_item`
- Notification target: `liusenlin.0927@bytedance.com`
- Keep `tag` and `length limit` blank by default

## Data Flow

1. Read Figma design context for a node or page.
2. Extract visible text nodes plus ancestor metadata needed for context and screenshot selection.
3. For each text row, select the nearest ancestor container that is large enough to explain usage but not so large that it becomes a whole-page screenshot.
4. Generate semantic key and context.
5. Capture screenshot for the selected container node and persist the local `screenshot_path`.
6. Create a Feishu sheet, write text columns, upload screenshots, and place them into the `screenshots` column.
7. Grant the configured target user access to the spreadsheet.
8. Send a Feishu message with the final spreadsheet link.

## Screenshot Selection

The screenshot is not a tight crop around the text itself. It should show where the copy is used.

Selection rules:

1. Start from the text node's direct parent.
2. Prefer the nearest ancestor whose type is container-like (`FRAME`, `GROUP`, `COMPONENT`, `INSTANCE`, `SECTION`).
3. Reject nodes that are too small to explain usage.
4. Reject nodes that are too large relative to the page.
5. Prefer names with semantic hints such as `button`, `input`, `field`, `card`, `modal`, `dialog`, `section`, `panel`, `empty`, `form`, `header`, `footer`.
6. Fall back to the page or top frame if no better candidate is found.

## Key Generation

Keys follow `page_module_item`.

Inputs:

- `page`: nearest page or top frame semantic name
- `module`: nearest selected container semantic name
- `item`: inferred role from the copy and node metadata

Role inference is intentionally simple for v1:

- `title`
- `subtitle`
- `button`
- `placeholder`
- `label`
- `helper`
- `description`
- `empty_state`
- fallback `text`

## Context Format

Use a compact, stable format so spreadsheet readers can audit keys quickly:

`page=<page>; module=<module>; role=<role>; text=<source_text>`

## Feishu Output

Sheet layout:

1. `A1`: namespace value
2. `A2:F2`: `keys | screenshots | tag | length limit | Context | Source`
3. Data starts at row 3

Write order:

1. Create sheet
2. Write namespace and headers
3. Batch write text cells in template order
4. Upload screenshot images and place them into column B one row at a time with `sheet image add --range "B{row}:B{row}"`; keep screenshot cells empty because the implementation uses anchored floating images
5. Grant `liusenlin.0927@bytedance.com` full access with `perm add --doc-type sheet`
6. Send notification message with row count and link

Image placement rules:

- Data row `0` maps to sheet row `3`, so its screenshot range is `<sheet_id>!B3:B3`.
- Data row `n` maps to sheet row `n + 3`, so never reuse the same anchor range for multiple screenshots.
- Include the sheet id prefix in `sheet image add --range`; bare ranges can fail with `Wrong Sheet Id`.
- Compute display width and height from the original image ratio before calling `sheet image add`; do not stretch screenshots to arbitrary fixed dimensions.
- Upload screenshots with `--parent-type sheet_image`, not `docx_image`, because sheet floating images require sheet-compatible image tokens.
- Verify insertion with `sheet image list <spreadsheet_token> <sheet_id>` and treat an empty list as screenshot placement failure.
- If default `feishu-cli` config loading reports missing credentials even though `~/.feishu-cli/config.yaml` exists, retry with `feishu-cli --config "$HOME/.feishu-cli/config.yaml" ...` and use that explicit config for the rest of the run.
- Treat `screenshot_node_id` plus empty `screenshot_path` as a failed intermediate state. It means selection happened but screenshot capture did not persist an uploadable file.

## Failure Policy

- If a fine-grained container is unavailable, use a larger ancestor and keep going.
- If screenshot generation fails for one row, leave that cell empty and continue.
- If image placement fails after sheet creation, return the sheet link and mention the partial failure.
- If permission grant fails after sheet creation, return the sheet link and mention that the user may not be able to open it yet.
- If Feishu notification fails, still return the link in chat.

## Acceptance Criteria

- Skill instructions clearly explain when to trigger.
- Scripts cover deterministic parts: key generation, screenshot node selection, row building.
- Eval prompts cover login, publish dialog, and empty state cases.
- Skill validates with the local quick validator.
- Python helper scripts compile successfully.
