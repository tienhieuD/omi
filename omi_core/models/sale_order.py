from odoo import api, models, fields

import logging
_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def unlink(self):
        product_point_id = self.env['ir.config_parameter'].sudo().get_param('omi_point_product', False)
        scale = self.env['ir.config_parameter'].sudo().get_param('omi_point_scale', 100)
        for rec in self:
            if rec.product_id.id == int(product_point_id):
                rec.order_id.partner_id.add_point(-(rec.price_unit / scale))
        return super(SaleOrderLine, self).unlink()


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    partner_point = fields.Float('Điểm khách hàng', related='partner_id.point')

    @api.model
    def default_get(self, fields):
        res = super(SaleOrder, self).default_get(fields)
        channel_id = self._context.get('channel_to_default')
        if channel_id and isinstance(channel_id, int):
            partner_ids = self.env['mail.channel'].browse(channel_id).channel_partner_ids.filtered('psid').ids
            res['partner_id'] = partner_ids[0]
        return res

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        """ Seach order base on chat channel_id """
        channel_id = self._context.get('channel_id_to_domain')
        if channel_id and isinstance(channel_id, int):
            partner_ids = self.env['mail.channel'].browse(channel_id).channel_partner_ids.ids
            domain += [('partner_id', 'in', partner_ids)]
        return super(SaleOrder, self).search_read(domain, fields, offset, limit, order)

    @api.multi
    def action_done(self):
        res = super(SaleOrder, self).action_done()
        scale = self.env['ir.config_parameter'].sudo().get_param('omi_point_scale', 100)
        for rec in self:
            rec.partner_id.add_point(rec.amount_total/scale)
        return res

    @api.multi
    def apply_point(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'apply.point.form',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref('omi_core.apply_point_form').id,
            'target': 'new',
            'context': {
                'default_partner_id': self.partner_id.id,
                'default_order_id': self.id,
            },
        }
