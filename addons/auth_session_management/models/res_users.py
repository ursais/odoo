# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    # Track when password was last changed for OAuth users
    oauth_password_changed = fields.Datetime(
        string='OAuth Password Changed',
        help='Timestamp when password was last changed for OAuth users',
        readonly=True
    )

    def _get_session_token_fields(self):
        """
        Override to exclude password field for OAuth users to prevent
        session invalidation when passwords are reset externally.
        """
        fields = super(ResUsers, self)._get_session_token_fields()
        
        # Check if we should preserve sessions for OAuth users
        preserve_oauth = self.env['ir.config_parameter'].sudo().get_param(
            'auth_session_management.preserve_oauth_sessions', 'True'
        ) == 'True'
        
        # For OAuth users, exclude password from session token computation
        # to prevent session invalidation when passwords are reset externally
        if preserve_oauth and self._is_oauth_user():
            fields = fields - {'password'}
            if self.env['ir.config_parameter'].sudo().get_param(
                'auth_session_management.enable_session_debug', 'False'
            ) == 'True':
                _logger.debug(
                    'Excluding password from session token for OAuth user %s (ID: %s)',
                    self.login, self.id
                )
        
        return fields

    def _is_oauth_user(self):
        """
        Check if the current user is authenticated via OAuth.
        """
        return bool(self.oauth_provider_id and self.oauth_uid)

    def _is_ldap_user(self):
        """
        Check if the current user is authenticated via LDAP.
        """
        # Check if user has LDAP configuration
        return bool(self.env['res.company.ldap'].search([]))

    def _change_password(self, new_passwd):
        """
        Override to track password changes for OAuth users and handle
        session management appropriately.
        """
        # Call parent method first
        super(ResUsers, self)._change_password(new_passwd)
        
        # For OAuth users, update the password change timestamp
        # but don't invalidate existing sessions
        if self._is_oauth_user():
            self.write({
                'oauth_password_changed': fields.Datetime.now()
            })
            _logger.info(
                'Password changed for OAuth user %s (ID: %s). '
                'Existing sessions will be preserved.',
                self.login, self.id
            )

    @api.model
    def change_password(self, old_passwd, new_passwd):
        """
        Override to handle OAuth users specially during password changes.
        """
        # For OAuth users, we don't need to validate the old password
        # since they're authenticated via external provider
        if self.env.user._is_oauth_user():
            if not new_passwd:
                raise UserError("New password cannot be empty")
            
            # Update password without validating old password
            self.env.user._change_password(new_passwd)
            return True
        
        # For regular users, use standard password change logic
        return super(ResUsers, self).change_password(old_passwd, new_passwd)

    def _compute_session_token(self, sid):
        """
        Override to use improved session token computation for OAuth users.
        """
        # Check configuration for session preservation
        preserve_oauth = self.env['ir.config_parameter'].sudo().get_param(
            'auth_session_management.preserve_oauth_sessions', 'True'
        ) == 'True'
        
        # For OAuth users, use a modified approach that's more stable
        if preserve_oauth and self._is_oauth_user():
            return self._compute_oauth_session_token(sid)
        
        # For regular users, use standard computation
        return super(ResUsers, self)._compute_session_token(sid)

    def _compute_oauth_session_token(self, sid):
        """
        Compute session token for OAuth users using a more stable approach.
        This prevents session invalidation when passwords are reset externally.
        """
        import hmac
        import hashlib
        
        # Use fields that are stable for OAuth users (exclude password)
        stable_fields = {'id', 'login', 'active', 'oauth_provider_id', 'oauth_uid'}
        session_fields = ', '.join(sorted(stable_fields))
        
        self.env.cr.execute("""
            SELECT %s, (SELECT value FROM ir_config_parameter WHERE key='database.secret')
            FROM res_users
            WHERE id=%%s
        """ % (session_fields), (self.id,))
        
        if self.env.cr.rowcount != 1:
            self.clear_caches()
            return False
        
        data_fields = self.env.cr.fetchone()
        
        # Generate HMAC key
        key = (u'%s' % (data_fields,)).encode('utf-8')
        
        # HMAC the session id
        data = sid.encode('utf-8')
        h = hmac.new(key, data, hashlib.sha256)
        
        return h.hexdigest()

    def _invalidate_sessions_for_password_change(self):
        """
        Override to prevent session invalidation for OAuth users.
        """
        # Check configuration
        preserve_oauth = self.env['ir.config_parameter'].sudo().get_param(
            'auth_session_management.preserve_oauth_sessions', 'True'
        ) == 'True'
        
        # For OAuth users, don't invalidate sessions on password change
        if preserve_oauth and self._is_oauth_user():
            _logger.info(
                'Skipping session invalidation for OAuth user %s (ID: %s) '
                'to preserve active sessions',
                self.login, self.id
            )
            return
        
        # For regular users, use standard behavior
        super(ResUsers, self)._invalidate_sessions_for_password_change()

    @api.model
    def _login(self, db, login, password, user_agent_env):
        """
        Override to add context for OAuth users during login.
        """
        # Set context to skip password in session token for OAuth users
        if hasattr(self, '_is_oauth_user'):
            # This will be set in the OAuth authentication flow
            pass
        
        return super(ResUsers, self)._login(db, login, password, user_agent_env)
