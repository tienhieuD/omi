from odoo import api, models

import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

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
