# Screenshot Selection

## Goal

Capture where the copy is used, not just the text box itself.

## Preferred Node Types

Prefer the nearest ancestor with a container-like type:

- `FRAME`
- `GROUP`
- `COMPONENT`
- `INSTANCE`
- `SECTION`

## Reject Conditions

Reject a screenshot candidate when one of these is true:

- node is still a text-like node
- width is below `120`
- height is below `40`
- candidate covers almost the entire page and there is a smaller usable ancestor

## Name Hints

Prefer names containing:

- `button`
- `input`
- `field`
- `card`
- `modal`
- `dialog`
- `section`
- `panel`
- `empty`
- `form`
- `header`
- `footer`

These hints are tie-breakers, not hard requirements.

## Fallback Chain

1. nearest valid container
2. next larger ancestor container
3. top frame or page

## Practical Rule

When unsure, choose the smaller ancestor that still makes the copy's purpose obvious.

## Highlighted Screenshots

When a screenshot must visually mark the source copy, use geometry from Figma metadata:

- capture the selected screenshot node with `figma_get_screenshot`
- record the selected screenshot node's `absoluteBoundingBox` as `screenshot_bounds`
- record the text node's `absoluteBoundingBox` as `text_bounds`
- run `scripts/highlight_screenshot_text.py` to draw the box after capture

The highlight rectangle must be computed as:

```text
scale_x = image_width / screenshot_bounds.width
scale_y = image_height / screenshot_bounds.height
left = (text_bounds.x - screenshot_bounds.x) * scale_x
top = (text_bounds.y - screenshot_bounds.y) * scale_y
```

Never estimate highlight coordinates from recreated HTML, row order, or visual inspection. Those estimates can appear correct for short labels but drift for multiline descriptions because Figma line boxes, icons, padding, and screenshot scaling differ from the recreated layout.
