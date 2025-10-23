# -*- coding: utf-8 -*-
{
    'name': 'Advanced Session Management for OAuth/LDAP',
    'version': '1.0.0',
    'category': 'Authentication',
    'summary': 'Improved session management for OAuth and LDAP authentication',
    'description': """
Advanced Session Management for OAuth/LDAP
=========================================

This module provides improved session management for users authenticated via OAuth or LDAP.
It addresses issues where users get logged out unexpectedly after password resets or when
duplicating browser tabs.

Key Features:
- Preserves user sessions during password resets for OAuth users
- Configurable session management behavior
- Prevents unexpected logouts when duplicating tabs
- Maintains security while improving user experience

This module is particularly useful for organizations using Microsoft SSO or other OAuth
providers where password resets are managed externally.
    """,
    'author': 'Open Source Integrators Inc',
    'website': 'https://www.opensourceintegrators.com',
    'depends': [
        'base',
        'auth_oauth',
        'auth_ldap',
        'web',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/res_users_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
