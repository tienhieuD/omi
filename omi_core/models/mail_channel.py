# -*- coding: utf-8 -*-

from odoo import api, fields, models


class MailChannel(models.Model):
    _inherit = 'mail.channel'

    channel_type = fields.Selection(selection_add=[('fb', 'Facebook Messenger')])

    @api.model
    def channel_fetch_slot(self):
        values = super(MailChannel, self).channel_fetch_slot()
        my_partner_id = self.env.user.partner_id.id
        pinned_channels = self.env['mail.channel.partner'].search([('partner_id', '=', my_partner_id), ('is_pinned', '=', True)]).mapped('channel_id')
        values['channel_fb'] = self.search([('id', 'in', pinned_channels.ids), ('channel_partner_ids', '=', my_partner_id), ('channel_type', '=', 'fb'),]).channel_info()
        return values
