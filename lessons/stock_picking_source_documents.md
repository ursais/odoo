# Lessons: stock.picking source documents (Odoo 16)

- Repo is plain odoo/odoo 16.0. No custom_addons dir; root `addons/` is on the
  default addons_path, so new custom modules go under `addons/<module>` (this is
  NOT modifying a core module).
- The transfers list tree view is `stock.vpicktree` (id `vpicktree`). There is
  NO `view_picking_out_tree` in v16. Picking-type actions reuse `vpicktree`.
- `stock.picking.origin` is a single Char. Each `stock.move` keeps its own
  `origin`. To aggregate all source docs of a merged transfer, depend on
  `move_ids.origin` (source-agnostic; no Sale/Purchase dependency needed).
- `sale_ids` / `purchase_ids` do NOT exist on stock.picking. Only singular
  `sale_id` (sale_stock) and `purchase_id` (purchase_stock), and only if those
  modules are installed. Avoid coupling to them.
- Don't `position="replace"` the `origin` field in vpicktree: `l10n_it_stock_ddt`
  anchors on it with `position="after"`. Instead set origin `optional="hide"` and
  add the new field after it.
