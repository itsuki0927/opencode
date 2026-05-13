# Key Rules

## Goal

Generate readable semantic keys in `page_module_item` form.

## Format

- lowercase only
- underscore separated
- three semantic segments when possible: `page_module_item`
- if a useful fourth segment is needed, keep it concise

## Source Signals

Use these signals in order:

1. top frame or page name for `page`
2. nearest meaningful container for `module`
3. inferred text role for `item`

## Sanitization

- replace spaces and separators with `_`
- drop punctuation
- collapse repeated `_`
- trim leading and trailing `_`
- avoid digits unless they are truly semantic

## Role Hints

Map copy to one of these item suffixes when possible:

- `title`
- `subtitle`
- `button`
- `placeholder`
- `label`
- `helper`
- `description`
- `empty_state_title`
- `empty_state_description`
- fallback `text`

## Good Examples

- `login_form_email_placeholder`
- `login_form_submit_button`
- `publish_dialog_title`
- `publish_dialog_description`
- `profile_empty_state_title`

## Bad Examples

- `text_1`
- `label_2`
- `home_copy`
- `button_content`
- `modal_text`

## Duplicate Handling

- If the same semantic row appears multiple times in the same module, reuse the same key.
- If the same copy appears in different modules with different usage, generate different keys.
- If the generated key already exists for a different source text, append a short semantic suffix instead of an opaque number when possible.
