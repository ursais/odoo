# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    invoice_count = fields.Integer(
        "Invoice Count",
        compute='_compute_invoice_count',
    )
    vendor_bill_count = fields.Integer(
        "Vendor Bill Count",
        compute='_compute_vendor_bill_count',
    )

    @api.depends('line_ids')
    def _compute_invoice_count(self):
        """Optimized computation of invoice count with better query performance."""
        if not self:
            return
            
        sale_types = self.env['account.move'].get_sale_types(include_receipts=True)
        
        # Optimize: Use more efficient query with proper indexing
        query_string = """
            SELECT jsonb_object_keys(aml.analytic_distribution) as account_id,
                   COUNT(DISTINCT aml.move_id) as move_count
            FROM account_move_line aml
            JOIN account_move am ON am.id = aml.move_id
            WHERE am.state = 'posted'
              AND am.move_type = ANY(%s)
              AND aml.analytic_distribution IS NOT NULL
              AND aml.analytic_distribution != '{}'::jsonb
              AND EXISTS (
                  SELECT 1 FROM jsonb_object_keys(aml.analytic_distribution) AS key
                  WHERE key::int = ANY(%s)
              )
            GROUP BY jsonb_object_keys(aml.analytic_distribution)
        """
        
        self._cr.execute(query_string, (list(sale_types), list(self.ids)))
        data = {int(record.get('account_id')): record.get('move_count') for record in self._cr.dictfetchall()}
        
        for account in self:
            account.invoice_count = data.get(account.id, 0)

    @api.depends('line_ids')
    def _compute_vendor_bill_count(self):
        """Optimized computation of vendor bill count with better query performance."""
        if not self:
            return
            
        purchase_types = self.env['account.move'].get_purchase_types(include_receipts=True)
        
        # Optimize: Use more efficient query with proper indexing
        query_string = """
            SELECT jsonb_object_keys(aml.analytic_distribution) as account_id,
                   COUNT(DISTINCT aml.move_id) as move_count
            FROM account_move_line aml
            JOIN account_move am ON am.id = aml.move_id
            WHERE am.state = 'posted'
              AND am.move_type = ANY(%s)
              AND aml.analytic_distribution IS NOT NULL
              AND aml.analytic_distribution != '{}'::jsonb
              AND EXISTS (
                  SELECT 1 FROM jsonb_object_keys(aml.analytic_distribution) AS key
                  WHERE key::int = ANY(%s)
              )
            GROUP BY jsonb_object_keys(aml.analytic_distribution)
        """
        
        self._cr.execute(query_string, (list(purchase_types), list(self.ids)))
        data = {int(record.get('account_id')): record.get('move_count') for record in self._cr.dictfetchall()}
        
        for account in self:
            account.vendor_bill_count = data.get(account.id, 0)

    def action_view_invoice(self):
        """Optimized action to view customer invoices."""
        self.ensure_one()
        
        # Optimize: Use direct SQL query for better performance
        sale_types = self.env['account.move'].get_sale_types()
        query_string = """
            SELECT DISTINCT am.id
            FROM account_move_line aml
            JOIN account_move am ON am.id = aml.move_id
            WHERE am.move_type = ANY(%s)
              AND aml.analytic_distribution ? %s
        """
        
        self._cr.execute(query_string, (list(sale_types), str(self.id)))
        move_ids = [row[0] for row in self._cr.fetchall()]
        
        result = {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "domain": [('id', 'in', move_ids)],
            "context": {"create": False},
            "name": _("Customer Invoices"),
            'view_mode': 'tree,form',
        }
        return result

    def action_view_vendor_bill(self):
        """Optimized action to view vendor bills."""
        self.ensure_one()
        
        # Optimize: Use direct SQL query for better performance
        purchase_types = self.env['account.move'].get_purchase_types()
        query_string = """
            SELECT DISTINCT am.id
            FROM account_move_line aml
            JOIN account_move am ON am.id = aml.move_id
            WHERE am.move_type = ANY(%s)
              AND aml.analytic_distribution ? %s
        """
        
        self._cr.execute(query_string, (list(purchase_types), str(self.id)))
        move_ids = [row[0] for row in self._cr.fetchall()]
        
        result = {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "domain": [('id', 'in', move_ids)],
            "context": {"create": False},
            "name": _("Vendor Bills"),
            'view_mode': 'tree,form',
        }
        return result
