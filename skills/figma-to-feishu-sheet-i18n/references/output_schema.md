# Output Schema

## Spreadsheet Layout

Write the spreadsheet to match the provided localization template.

### Row 1

Write namespace in `A1`:

`namespace: <value>`

If no namespace is available yet, write `namespace:`.

### Row 2 headers

Write exactly these headers in order:

1. `keys`
2. `screenshots`
3. `tag`
4. `length limit`
5. `Context`
6. `Source`

## Row Shape

Internal row JSON should use:

```json
{
  "key": "login_form_email_placeholder",
  "source_text": "Enter your email",
  "context": "page=login; module=form; role=placeholder; text=Enter your email",
  "screenshot_node_id": "123:456",
  "screenshot_path": "/tmp/login-form-email.png",
  "text_bounds": {"x": 120, "y": 240, "width": 160, "height": 20},
  "screenshot_bounds": {"x": 96, "y": 200, "width": 320, "height": 180}
}
```

`screenshot_path` must be an existing local image file before image placement. Do not leave it empty when `screenshot_node_id` is present; empty paths mean screenshots were selected but never captured.

When highlighted screenshots are requested, keep `text_bounds` and `screenshot_bounds` in Figma absolute coordinates and run:

```bash
python3 skills/figma-to-feishu-sheet-i18n/scripts/highlight_screenshot_text.py rows.json highlighted-rows.json
```

Upload screenshot paths from `highlighted-rows.json`. Do not use manually estimated coordinates; they drift on multiline copy and lower-page text.

## Feishu Commands

### Create sheet

```bash
feishu-cli sheet create --title "Figma Copy Export - 2026-04-15"
```

### Write namespace, headers, and text columns

Use a simple matrix for columns `A:F`.

```bash
feishu-cli sheet write <sheet_token> "A1:F<N>" --sheet-id <sheet_id> --data '<json matrix>'
```

Where the matrix starts with:

```json
[
  ["namespace: https://starling.bytedance.net/project_detail/..."],
  ["keys", "screenshots", "tag", "length limit", "Context", "Source"],
  ["login_form_email_placeholder", "", "", "", "page=login; module=form; role=placeholder; text=Enter your email", "Enter your email"]
]
```

### Place image into screenshot cell

The current `feishu-cli` exposes sheet images as floating images. Treat every floating image as cell-anchored by passing a single-cell range.

1. Calculate display dimensions that preserve the original screenshot aspect ratio.
2. Upload the screenshot image as a sheet image and get an image token.
3. Place it in the target row with `sheet image add`.
4. Verify that the sheet contains floating images with `sheet image list`.

```bash
python3 skills/figma-to-feishu-sheet-i18n/scripts/prepare_sheet_image.py screenshot.png 320 180
feishu-cli media upload screenshot.png --parent-type sheet_image --parent-node <sheet_token> -o json
feishu-cli sheet image add <sheet_token> <sheet_id> \
  --token <image_token> \
  --range "<sheet_id>!B3:B3" \
  --width <computed_width> \
  --height <computed_height>
feishu-cli sheet image list <sheet_token> <sheet_id> -o json
```

Row mapping is strict:

```text
target_row = exported_row_index + 3
target_range = <sheet_id>!B{target_row}:B{target_row}
```

For example, if `sheet_id` is `8a9003`, exported rows `0`, `1`, and `2` map to `8a9003!B3:B3`, `8a9003!B4:B4`, and `8a9003!B5:B5`.

The sheet id prefix in `--range` is required by the V3 floating image API. Passing a bare range like `B7:B7` can fail with `Wrong Sheet Id`.

Do not use the older shorthand `feishu-cli sheet image <token> "B3" --image-token ...`; this CLI now requires the `add` subcommand and explicit `--range`.

Do not hardcode both width and height independently. Use dimensions from `prepare_sheet_image.py`; otherwise screenshots can be stretched.

Do not upload screenshots as `docx_image` for sheet placement. Use `sheet_image`; document-image tokens can fail to render in sheets. If `sheet_image` upload is rejected by the installed CLI/API, leave the screenshot cells empty, report screenshot placement as failed, and do not claim screenshots succeeded.

Use `scripts/build_sheet_image_commands.py` when placing many screenshots. It generates commands with the correct row offset and avoids accidentally reusing `B3:B3`.

If `build_sheet_image_commands.py` fails with `Rows have screenshot_node_id but empty screenshot_path`, go back to screenshot capture. Do not continue with sheet creation as if screenshots were attached.

## Notification Message

Send a Feishu message with:

- spreadsheet title
- exported row count
- spreadsheet link

Use:

- `receive_id_type=email`
- `receive_id=liusenlin.0927@bytedance.com`

## Permission Grant

Grant the target user access to the sheet after creation:

```bash
feishu-cli perm add <sheet_token> \
  --doc-type sheet \
  --member-type email \
  --member-id liusenlin.0927@bytedance.com \
  --perm edit \
  --notification
```

Permission APIs require App Token configuration. If `feishu-cli` reports `缺少 app_id 或 app_secret 配置`, stop and report missing App credentials; User OAuth is not enough for this operation.

If `~/.feishu-cli/config.yaml` exists but default loading still reports missing credentials, retry the same command with:

```bash
feishu-cli --config "$HOME/.feishu-cli/config.yaml" perm add <sheet_token> \
  --doc-type sheet \
  --member-type email \
  --member-id liusenlin.0927@bytedance.com \
  --perm full_access \
  --notification
```

If `perm update` lacks `docs:permission.member:update`, use `perm add` with the desired permission level. The create/add scope can still grant or overwrite the recipient permission.

## Chat Response

Always return:

1. spreadsheet link
2. row count
3. screenshot success status
4. notification success status
5. permission grant status
