# -*- coding: utf-8 -*-
{
    'name': 'MRP Mark as Done Multi-Record Fix',
    'version': '16.0.1.0.0',
    'category': 'Manufacturing/Manufacturing',
    'summary': 'Fixes singleton error when marking multiple MOs as done from list view',
    'description': """
Fixes ValueError: Expected singleton when using the "Mark as Done"
server action on multiple Manufacturing Orders selected in the list view.

The core button_mark_done method accesses picking_type_id.auto_show_reception_report
on a multi-record recordset, which raises a singleton error when the MOs have
different picking types. This module overrides the post-processing section to
iterate per-record where necessary.
    """,
    'depends': ['mrp'],
    'data': [],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
