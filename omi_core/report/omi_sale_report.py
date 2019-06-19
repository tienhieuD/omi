from odoo import tools
from odoo import api, fields, models


class OmiSaleReport(models.Model):
    _name = 'omi.sale.report'
    _auto = False
    _order = 'product_id'

    product_id = fields.Many2one('product.product', 'Sản phẩm')
    product_count = fields.Float('Số lượng sản phẩm')

    def _select(self):
        return """
            SELECT 
                min(l.id) as id,
                l.product_id as product_id,
                count(product_id) as product_count
        """

    def _from(self):
        from_str = """
            sale_order_line l 
                join sale_order s on(l.order_id=s.id)
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY 
                l.id,
                l.product_id
        """
        return group_by_str

    @api.model_cr
    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM ( %s )
            %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))


