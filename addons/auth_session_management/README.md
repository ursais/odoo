# Advanced Session Management for OAuth/LDAP

This module provides improved session management for users authenticated via OAuth or LDAP, specifically addressing issues with Microsoft SSO (MSFT SSO) where users get logged out unexpectedly after password resets.

## Problem Description

The original issue occurs when:
1. Users are authenticated via OAuth (like Microsoft SSO) or LDAP
2. Passwords are reset externally (e.g., by an administrator)
3. Users get logged out from all active sessions, including when duplicating browser tabs
4. Users experience "forced login" prompts and session timeouts during active work

## Root Cause

Odoo's session token computation includes the `password` field in the session token calculation. When passwords are reset externally, the password field changes, invalidating all existing session tokens and forcing users to log in again.

## Solution

This module implements a more granular session management approach that:

1. **Excludes password from session tokens for OAuth users** - Prevents session invalidation when passwords are reset externally
2. **Provides configuration options** - Allows administrators to control session management behavior
3. **Maintains security** - Still validates user credentials through OAuth providers
4. **Adds debugging capabilities** - Helps troubleshoot authentication issues

## Key Features

- **Session Preservation**: OAuth users maintain their sessions even after external password resets
- **Configurable Behavior**: Settings to enable/disable session preservation for different authentication methods
- **Debug Logging**: Detailed logging for troubleshooting authentication issues
- **OAuth Token Validation**: Automatic validation of OAuth access tokens
- **Session Monitoring**: Tools to check session status and validity

## Installation

1. Copy this module to your Odoo addons directory
2. Update the module list in Odoo
3. Install the "Advanced Session Management for OAuth/LDAP" module
4. Configure the settings in Settings > General Settings > Session Management

## Configuration

After installation, you can configure the module in:
**Settings > General Settings > Session Management**

Available settings:
- **Preserve OAuth Sessions**: Enable/disable session preservation for OAuth users
- **Preserve LDAP Sessions**: Enable/disable session preservation for LDAP users  
- **Session Timeout Warning**: Show warnings before session expires (in minutes)
- **Enable Session Debug Logging**: Enable detailed logging for troubleshooting

## Usage

### For OAuth Users
- Sessions will be preserved when passwords are reset externally
- No more unexpected logouts when duplicating browser tabs
- No more "forced login" prompts during active work

### For Administrators
- Monitor OAuth user password changes in the user form
- Use debug tools to troubleshoot authentication issues
- Configure session management behavior as needed

## API Endpoints

The module provides several JSON-RPC endpoints for session management:

- `/web/session/check_oauth_status` - Check OAuth user status
- `/web/session/refresh_oauth_token` - Refresh OAuth access token
- `/web/session/debug_session` - Debug session information (requires debug mode)

## Technical Details

### Session Token Computation
For OAuth users, the module uses a modified session token computation that excludes the password field, using instead:
- User ID
- Login
- Active status
- OAuth Provider ID
- OAuth UID

This ensures that external password changes don't invalidate existing sessions.

### Security Considerations
- OAuth users are still authenticated through their OAuth provider
- Session tokens are still cryptographically secure
- Password changes are tracked and logged
- Debug mode can be disabled in production

## Troubleshooting

### Enable Debug Logging
1. Go to Settings > General Settings > Session Management
2. Enable "Enable Session Debug Logging"
3. Check the Odoo logs for detailed session information

### Check Session Status
Use the debug endpoint to check session information:
```javascript
odoo.rpc('/web/session/debug_session').then(function(result) {
    console.log('Session Debug Info:', result);
});
```

### Common Issues
1. **Sessions still being invalidated**: Check that "Preserve OAuth Sessions" is enabled
2. **OAuth token errors**: Verify OAuth provider configuration
3. **Debug information not available**: Ensure debug logging is enabled

## Compatibility

- Odoo 15.0+
- Compatible with auth_oauth and auth_ldap modules
- Works with Microsoft SSO and other OAuth providers

## Support

For issues or questions regarding this module, please contact Open Source Integrators Inc.

## License

LGPL-3
