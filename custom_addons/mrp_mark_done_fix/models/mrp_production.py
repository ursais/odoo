# -*- coding: utf-8 -*-

from odoo import fields, models, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def button_mark_done(self):
        """Override to fix singleton error when marking multiple MOs as done.

        The core method accesses self.picking_type_id.auto_show_reception_report
        and self.id on a multi-record recordset in the post-processing section,
        which raises ValueError: Expected singleton.
        """
        self._button_mark_done_sanity_checks()

        if not self.env.context.get('button_mark_done_production_ids'):
            self = self.with_context(button_mark_done_production_ids=self.ids)
        res = self._pre_button_mark_done()
        if res is not True:
            return res

        if self.env.context.get('mo_ids_to_backorder'):
            productions_to_backorder = self.browse(self.env.context['mo_ids_to_backorder'])
            productions_not_to_backorder = self - productions_to_backorder
        else:
            productions_not_to_backorder = self
            productions_to_backorder = self.env['mrp.production']

        self.workorder_ids.button_finish()

        backorders = productions_to_backorder and productions_to_backorder._split_productions()
        backorders = backorders - productions_to_backorder

        productions_not_to_backorder._post_inventory(cancel_backorder=True)
        productions_to_backorder._post_inventory(cancel_backorder=True)

        done_move_finished_ids = (
            productions_to_backorder.move_finished_ids
            | productions_not_to_backorder.move_finished_ids
        ).filtered(lambda m: m.state == 'done')
        done_move_finished_ids._trigger_assign()

        (productions_not_to_backorder.move_raw_ids
         | productions_not_to_backorder.move_finished_ids
        ).filtered(lambda x: x.state not in ('done', 'cancel')).write({
            'state': 'done',
            'product_uom_qty': 0.0,
        })
        for production in self:
            production.write({
                'date_finished': fields.Datetime.now(),
                'product_qty': production.qty_produced,
                'priority': '0',
                'is_locked': True,
                'state': 'done',
            })

        if not backorders:
            if self.env.context.get('from_workorder'):
                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'mrp.production',
                    'views': [[self.env.ref('mrp.mrp_production_form_view').id, 'form']],
                    'res_id': self[:1].id,
                    'target': 'main',
                }
            if self.user_has_groups('mrp.group_mrp_reception_report') \
                    and any(mo.picking_type_id.auto_show_reception_report for mo in self):
                lines = self.move_finished_ids.filtered(
                    lambda m: m.product_id.type == 'product'
                    and m.state != 'cancel'
                    and m.quantity_done
                    and not m.move_dest_ids
                )
                if lines:
                    if any(mo.show_allocation for mo in self):
                        action = self.action_view_reception_report()
                        return action
            return True
        context = self.env.context.copy()
        context = {k: v for k, v in context.items() if not k.startswith('default_')}
        for k, v in context.items():
            if k.startswith('skip_'):
                context[k] = False
        action = {
            'res_model': 'mrp.production',
            'type': 'ir.actions.act_window',
            'context': dict(context, mo_ids_to_backorder=None, button_mark_done_production_ids=None)
        }
        if len(backorders) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': backorders[0].id,
            })
        else:
            action.update({
                'name': _("Backorder MO"),
                'domain': [('id', 'in', backorders.ids)],
                'view_mode': 'tree,form',
            })
        return action
