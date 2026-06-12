from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    source_document_list = fields.Char(
        string='Source Documents',
        compute='_compute_source_document_list',
        store=True,
        help="All source documents linked to this transfer. When several "
             "documents (e.g. multiple sales or purchase orders) are merged "
             "into a single transfer, every distinct source document is listed "
             "here instead of only the first one.",
    )

    @api.depends('origin', 'move_ids.origin')
    def _compute_source_document_list(self):
        """Aggregate the distinct source documents of a transfer.

        The transfer's own ``origin`` and the ``origin`` of each related stock
        move are collected, de-duplicated while preserving their order, and
        joined into a single comma separated string. Relying on the stock moves
        keeps the field source-agnostic: it works for sales, purchases,
        manufacturing or internal transfers without depending on those modules.
        """
        for picking in self:
            origins = []
            if picking.origin:
                origins.append(picking.origin)
            for move in picking.move_ids:
                if move.origin and move.origin not in origins:
                    origins.append(move.origin)
            picking.source_document_list = ', '.join(origins) if origins else False
