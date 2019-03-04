# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    psid = fields.Char("Facebook Page Sender ID")
    page_id = fields.Char("Facebook Page ID")

    @api.model
    def get_create_user_from_psid(self, psid, page_id):
        """ Từ sender page id truyền vào, tìm ra người dùng xem đã có trên hệ thống hay chưa?
            Không có thì tạo mới...
        """
        user = self.search([('psid', '=', psid), ('page_id', '=', page_id)])
        if user: return user

        FacebookUtils = self.env['omi.facebook.utils']
        user_info = FacebookUtils.get_sender_info(page_id=page_id, sender_id=psid)
        user_name = user_info['first_name'] + ' ' + user_info['last_name']
        # TODO: Làm hình người dùng sau
        # image = user_info['profile_pic']
        user = self.sudo().create({'name': user_name, 'psid': psid, 'page_id': page_id,})
        return user

