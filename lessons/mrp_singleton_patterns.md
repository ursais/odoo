# MRP Singleton Access Patterns (Odoo 16)

## Discovery
`button_mark_done` in `mrp.production` has singleton assumptions in its post-processing return logic (lines 1916-1919). This breaks when the method is called via the list-view server action on multiple records.

## Key Patterns
- `self.picking_type_id.auto_show_reception_report` on multi-record self: fails because `self.picking_type_id` returns a multi-record picking type set, and `.auto_show_reception_report` (boolean) requires singleton.
- `self.id` on multi-record self: always fails.
- Fix: iterate per-record with `any(mo.field for mo in self)` or use `self[:1].id` where appropriate.

## Approach
Since core cannot be modified, override the entire method in a custom module. The helper methods (`_button_mark_done_sanity_checks`, `_pre_button_mark_done`, `_post_inventory`, etc.) are all recordset-safe; only the return logic section needs fixing.
