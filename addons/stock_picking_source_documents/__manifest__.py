{
    'name': 'Stock Picking - Aggregated Source Documents',
    'version': '16.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Show all source documents of a transfer in the list view',
    'description': """
Aggregated Source Documents on Transfers
========================================

The standard "Source Document" (``origin``) field on a transfer (``stock.picking``)
is a single text value. When several source documents (for example multiple sales
orders, purchase orders or other transfers) are merged into a single receipt or
delivery, only one of them is shown in the list view.

This module adds a computed field that collects the source documents of every
stock move linked to the transfer (plus the transfer's own ``origin``) and exposes
them as a single, de-duplicated, comma separated value in the transfers list view.

The solution relies only on the ``stock`` module, so it works regardless of which
source modules (Sales, Purchase, Manufacturing, ...) are installed.
""",
    'author': 'Open Source Integrators',
    'website': 'https://www.opensourceintegrators.com',
    'license': 'LGPL-3',
    'depends': ['stock'],
    'data': [
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
