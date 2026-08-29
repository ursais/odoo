# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Spreadsheet Save Status Fix",
    "version": "17.0.1.0.0",
    "category": "Tools",
    "summary": "Fix false 'saved' status indication in Odoo Spreadsheets",
    "description": """
        This module fixes an issue where Odoo Spreadsheets falsely indicates
        'saved' status when changes are not actually persisted to the database.
        
        The fix ensures that the 'saved' indicator only updates after confirming
        successful data write to the backend, preventing premature status updates.
        
        Technical Details:
        ------------------
        The original SpreadsheetCollaborativeChannel.sendMessage() method would
        immediately acknowledge messages locally when the server accepted them,
        before the server had actually persisted the data and broadcast it back.
        This caused the 'saved' status to show prematurely.
        
        This fix removes the premature local notification and relies solely on
        the server's broadcast via the bus channel, which only happens after
        successful persistence.
    """,
    "depends": ["spreadsheet_edition"],
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "LGPL-3",
    "assets": {
        "web.assets_backend": [
            "spreadsheet_save_status_fix/static/src/bundle/o_spreadsheet/collaborative/spreadsheet_collaborative_channel.js",
            "spreadsheet_save_status_fix/static/src/bundle/o_spreadsheet/collaborative/spreadsheet_collaborative_service.js",
        ],
    },
}
