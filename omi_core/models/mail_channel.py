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

    @api.model
    def get_create_channel_from_author(self, partner_id):
        """ Tìm kênh chát của người dùng facebook, nếu chưa có tạo mới một cái """
        self = self.sudo()
        channel = self.search([('channel_partner_ids', '=', partner_id), ('channel_type', '=', 'fb')], limit=1)
        if not channel:
            channel = self.with_context(mail_create_nosubscribe=False).create({
                'channel_partner_ids': [(6, 0, [partner_id, 4])],
                'channel_type': 'fb',
                'name': self.env['res.partner'].browse(partner_id).display_name,
                'public': 'private',
                'email_send': False,
            })
        return channel
