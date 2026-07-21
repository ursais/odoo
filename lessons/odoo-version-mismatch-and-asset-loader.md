# Odoo ticket lessons

## Ticket error version can differ from the checked-out repo
- Ticket 89414 ("Pink screen opening SO") referenced `OptionalFieldsDropdown`,
  `listRendererClass`, and `web.assets_web_dark` — all Odoo 17/18 constructs —
  but the repo was checked out at Odoo 16.0 (`odoo/release.py` → `(16,0,...)`).
- Signals to confirm version quickly: `odoo/release.py`, `addons/web/__manifest__.py`.
- Dark mode ("monkey turned on" in user speak) + `assets_web_dark` ⇒ 17.4+/18.

## Odoo JS module loader tolerates MISSING imports (no crash)
- In `addons/web/static/src/boot.js`, a module whose `@web/...` import is not
  defined becomes a "Non loaded module" (info-level log). It does NOT throw and
  does NOT break the rest of the web client. Only a thrown error in a factory is
  a "Failed module".
- Practical upshot: a custom asset that `import`s a component which only exists in
  a newer Odoo (e.g. `@web/views/list/optional_fields_dropdown/...`) is a safe
  no-op on older versions — the module just isn't loaded. This lets one module
  target the version where the bug lives without breaking the snapshot version.

## `patch()` API differs by version
- Odoo 16: `patch(obj, patchName, patchValue)` (see `web/core/utils/patch.js`).
- Odoo 17+: `patch(obj, patchValue)`.
- For adjusting a component's static `props`/`defaultProps`, prefer direct
  assignment with spread (version-agnostic) over `patch()`.

## Repo layout
- No dedicated custom-addons dir; addons path is `addons/`. Modules named
  `payment_custom` / `website_customer` in `addons/` are CORE, not customer code.
