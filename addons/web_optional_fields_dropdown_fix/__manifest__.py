# -*- coding: utf-8 -*-
{
    "name": "Web Optional Fields Dropdown Fix",
    "version": "16.0.1.0.0",
    "category": "Technical",
    "summary": "Make the list optional-columns dropdown resilient to a missing "
               "'listRendererClass' prop (fixes a pink/error screen when opening "
               "records, e.g. Sales Orders, in debug + dark mode).",
    "description": """
Web Optional Fields Dropdown Fix
================================

Some list views (notably the Sales Order / Invoice line lists that use the
section-and-note renderer) crash with an OwlError when the ``OptionalFieldsDropdown``
component is rendered without the ``listRendererClass`` prop::

    Invalid props for component 'OptionalFieldsDropdown':
    'listRendererClass' is missing (should be a string)

This happens in specific contexts (for instance developer/debug mode combined
with the dark theme, or with customised list renderers that do not forward every
prop). The crash blanks the record form entirely.

This module patches the ``OptionalFieldsDropdown`` component so that
``listRendererClass`` is an optional prop with a safe default, which lets OWL's
prop validation pass and the list render normally regardless of the caller.

Notes
-----
``OptionalFieldsDropdown`` was introduced in Odoo 17. On Odoo 16 (where the
optional-columns dropdown is still inlined in the list renderer template) the
imported component does not exist, so this asset is simply skipped by the module
loader and the module is an inert no-op -- it never breaks the web client.
""",
    "author": "Open Source Integrators",
    "website": "https://www.opensourceintegrators.com",
    "license": "LGPL-3",
    "depends": ["web"],
    "assets": {
        "web.assets_backend": [
            "web_optional_fields_dropdown_fix/static/src/js/optional_fields_dropdown_patch.js",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
