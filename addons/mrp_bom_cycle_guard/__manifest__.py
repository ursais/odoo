# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'MRP BOM Cycle Guard',
    'version': '16.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Prevents infinite loops in BOM computation due to circular dependencies',
    'description': """
MRP BOM Cycle Guard
===================

This module enhances the BOM (Bill of Materials) explosion mechanism to prevent
504 Gateway Timeout errors caused by circular dependencies in BOM structures.

Features:
---------
* Implements robust recursion depth tracking to prevent infinite loops
* Adds early cycle detection during BOM explosion
* Provides clear error messages when circular dependencies are detected
* Improves performance by optimizing cycle detection algorithm
* Adds logging for debugging BOM computation issues

Technical Details:
------------------
The module overrides the explode() method in mrp.bom model to add:
- Maximum recursion depth limit (configurable, default 100)
- Visited products tracking to detect cycles early
- Enhanced error reporting with product chain information
    """,
    'author': 'Damage Control QA',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'mrp',
    ],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
