from odoo import api, fields, models
from odoo.exceptions import UserError


class PointForm(models.TransientModel):
    _name = 'point.form'
    _description = 'Add point form'

    point = fields.Float('Số điểm cần thêm', default=0)
    partner_id = fields.Many2one('res.partner', string='Khách hàng', required=True)

    @api.multi
    def action_apply(self):
        self.ensure_one()
        if not self.partner_id:
            raise UserError('Cần nhập khách hàng')
        return self.partner_id.add_point(self.point)


class ApplyPointForm(models.Model):
    _name = 'apply.point.form'
    _inherit = 'point.form'

    order_id = fields.Many2one('sale.order', 'Đơn hàng', required=True)

    @api.multi
    def action_apply_point(self):
        self.ensure_one()
        if not self.partner_id or not self.order_id:
            raise UserError('Cần nhập khách hàng / đơn hàng')

        if self.partner_id.point < self.point:
            raise UserError('Khách không đủ điểm để áp dụng, tối đa %s' % self.partner_id.point)

        point_product_id = self.env['ir.config_parameter'].sudo().get_param('omi_point_product', False)
        if not point_product_id:
            raise UserError('Chưa cấu hình sản phẩm giảm giá (product.product) <omi_point_product>')

        scale = self.env['ir.config_parameter'].sudo().get_param('omi_point_scale', 100)
        point = min(self.partner_id.point, self.point, self.order_id.amount_total/scale)

        sale_order_line = self.env['sale.order.line'].create({
            'name': "Áp dụng điểm",
            'product_id': int(point_product_id),
            'product_uom_qty': 1,
            'price_unit': -(point * scale),
            'order_id': self.order_id.id,
        })

        self.order_id.partner_id.sub_point(point)

        return sale_order_line
