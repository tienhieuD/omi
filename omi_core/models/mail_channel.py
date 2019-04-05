from odoo import api, fields, models
from odoo.tools import html2plaintext


class MailChannel(models.Model):
    _inherit = 'mail.channel'

    channel_type = fields.Selection(selection_add=[('fb', 'Facebook Messenger')])

    @api.model
    def channel_fetch_slot(self):
        values = super(MailChannel, self).channel_fetch_slot()
        my_partner_id = self.env.user.partner_id.id
        pinned_channels = self.env['mail.channel.partner'].search([
            ('partner_id', '=', my_partner_id),
            ('is_pinned', '=', True)
        ]).mapped('channel_id')
        values['channel_fb'] = self.search([
            ('id', 'in', pinned_channels.ids),
            ('channel_partner_ids', '=', my_partner_id),
            ('channel_type', '=', 'fb')
        ]).channel_info()
        return values

    @api.model
    def get_create_channel_from_author(self, partner_id):
        """ Tìm kênh chát của người dùng facebook, nếu chưa có tạo mới một cái """
        self = self.sudo()
        channel = self.search([
            ('channel_partner_ids', '=', partner_id),
            ('channel_type', '=', 'fb')
        ], limit=1)
        if not channel:
            # TODO: Mặc định đang lấy partner gửi tin đến và Admin root (ID 3)
            channel = self.with_context(mail_create_nosubscribe=False).create({
                'channel_partner_ids': [(6, 0, [partner_id, 3])],
                'channel_type': 'fb',
                'name': self.env['res.partner'].browse(partner_id).display_name,
                'public': 'private',
                'email_send': False,
            })
        return channel

    @api.multi
    @api.returns('self', lambda value: value.id)
    def message_post(self, **kwargs):
        """ Gửi tin từ odoo -> facebook
            TODO: if sender in [list_of_fb_manager]  // trường hợp nhiều fbmanager cho 1 kênh """
        res = super(MailChannel, self).message_post(**kwargs)
        if not res.author_id.psid:  # không phải người dùng facebook
            send_message = self.env['omi.facebook.utils'].send_message
            recipients = self.channel_partner_ids - res.author_id
            for recipient in recipients:
                send_message(partner=recipient, text=html2plaintext(res.body))
        return res
