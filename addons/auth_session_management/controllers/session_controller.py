# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class SessionController(http.Controller):

    @http.route('/web/session/get_session_info', type='json', auth="user")
    def get_session_info(self):
        """
        Override to add session management information for OAuth users.
        """
        # Get standard session info
        session_info = request.env['ir.http'].session_info()
        
        # Add OAuth-specific information
        if request.env.user._is_oauth_user():
            session_info.update({
                'is_oauth_user': True,
                'oauth_provider': request.env.user.oauth_provider_id.name if request.env.user.oauth_provider_id else None,
                'oauth_password_changed': request.env.user.oauth_password_changed.isoformat() if request.env.user.oauth_password_changed else None,
                'session_preserved': True,
            })
        else:
            session_info.update({
                'is_oauth_user': False,
                'session_preserved': False,
            })
        
        return session_info

    @http.route('/web/session/check_oauth_status', type='json', auth="user")
    def check_oauth_status(self):
        """
        Check OAuth user status and session validity.
        """
        user = request.env.user
        
        if not user._is_oauth_user():
            return {
                'is_oauth': False,
                'message': 'User is not authenticated via OAuth'
            }
        
        # Check if session preservation is enabled
        preserve_oauth = request.env['ir.config_parameter'].sudo().get_param(
            'auth_session_management.preserve_oauth_sessions', 'True'
        ) == 'True'
        
        return {
            'is_oauth': True,
            'oauth_provider': user.oauth_provider_id.name if user.oauth_provider_id else None,
            'oauth_uid': user.oauth_uid,
            'password_changed': user.oauth_password_changed.isoformat() if user.oauth_password_changed else None,
            'session_preserved': preserve_oauth,
            'message': 'OAuth user session is being preserved' if preserve_oauth else 'OAuth user session preservation is disabled'
        }

    @http.route('/web/session/refresh_oauth_token', type='json', auth="user")
    def refresh_oauth_token(self):
        """
        Refresh OAuth access token if needed.
        """
        user = request.env.user
        
        if not user._is_oauth_user():
            return {
                'success': False,
                'message': 'User is not authenticated via OAuth'
            }
        
        try:
            # Validate current OAuth token
            if user.oauth_access_token:
                validation = user._auth_oauth_validate(
                    user.oauth_provider_id.id, 
                    user.oauth_access_token
                )
                
                if validation.get('error'):
                    return {
                        'success': False,
                        'message': 'OAuth token is invalid or expired',
                        'error': validation['error']
                    }
            
            return {
                'success': True,
                'message': 'OAuth token is valid',
                'token_valid': True
            }
            
        except Exception as e:
            _logger.exception("Error refreshing OAuth token for user %s", user.login)
            return {
                'success': False,
                'message': 'Error validating OAuth token',
                'error': str(e)
            }

    @http.route('/web/session/debug_session', type='json', auth="user")
    def debug_session(self):
        """
        Debug session information (only available when debug mode is enabled).
        """
        debug_enabled = request.env['ir.config_parameter'].sudo().get_param(
            'auth_session_management.enable_session_debug', 'False'
        ) == 'True'
        
        if not debug_enabled:
            return {
                'success': False,
                'message': 'Session debug is not enabled'
            }
        
        user = request.env.user
        session = request.session
        
        debug_info = {
            'user_id': user.id,
            'user_login': user.login,
            'is_oauth_user': user._is_oauth_user(),
            'oauth_provider': user.oauth_provider_id.name if user.oauth_provider_id else None,
            'oauth_uid': user.oauth_uid,
            'session_id': session.sid,
            'session_uid': session.uid,
            'session_token': session.session_token,
            'password_changed': user.oauth_password_changed.isoformat() if user.oauth_password_changed else None,
            'preserve_oauth_sessions': request.env['ir.config_parameter'].sudo().get_param(
                'auth_session_management.preserve_oauth_sessions', 'True'
            ) == 'True',
        }
        
        # Compute expected session token
        try:
            expected_token = user._compute_session_token(session.sid)
            debug_info['expected_token'] = expected_token
            debug_info['token_match'] = expected_token == session.session_token
        except Exception as e:
            debug_info['token_error'] = str(e)
        
        return {
            'success': True,
            'debug_info': debug_info
        }
