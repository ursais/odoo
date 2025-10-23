# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Session Management Settings
    preserve_oauth_sessions = fields.Boolean(
        string='Preserve OAuth Sessions',
        help='When enabled, OAuth users will not be logged out when passwords are reset externally. '
             'This prevents the "forced login" and "timeout" issues with MSFT SSO.',
        default=True,
        config_parameter='auth_session_management.preserve_oauth_sessions'
    )
    
    preserve_ldap_sessions = fields.Boolean(
        string='Preserve LDAP Sessions',
        help='When enabled, LDAP users will not be logged out when passwords are reset externally.',
        default=True,
        config_parameter='auth_session_management.preserve_ldap_sessions'
    )
    
    session_timeout_warning = fields.Integer(
        string='Session Timeout Warning (minutes)',
        help='Show warning to users when session is about to expire. Set to 0 to disable.',
        default=5,
        config_parameter='auth_session_management.session_timeout_warning'
    )
    
    enable_session_debug = fields.Boolean(
        string='Enable Session Debug Logging',
        help='Enable detailed logging for session management operations. '
             'Useful for troubleshooting authentication issues.',
        default=False,
        config_parameter='auth_session_management.enable_session_debug'
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            preserve_oauth_sessions=self.env['ir.config_parameter'].sudo().get_param(
                'auth_session_management.preserve_oauth_sessions', 'True'
            ) == 'True',
            preserve_ldap_sessions=self.env['ir.config_parameter'].sudo().get_param(
                'auth_session_management.preserve_ldap_sessions', 'True'
            ) == 'True',
            session_timeout_warning=int(self.env['ir.config_parameter'].sudo().get_param(
                'auth_session_management.session_timeout_warning', '5'
            )),
            enable_session_debug=self.env['ir.config_parameter'].sudo().get_param(
                'auth_session_management.enable_session_debug', 'False'
            ) == 'True',
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'auth_session_management.preserve_oauth_sessions', 
            str(self.preserve_oauth_sessions)
        )
        self.env['ir.config_parameter'].sudo().set_param(
            'auth_session_management.preserve_ldap_sessions', 
            str(self.preserve_ldap_sessions)
        )
        self.env['ir.config_parameter'].sudo().set_param(
            'auth_session_management.session_timeout_warning', 
            str(self.session_timeout_warning)
        )
        self.env['ir.config_parameter'].sudo().set_param(
            'auth_session_management.enable_session_debug', 
            str(self.enable_session_debug)
        )
