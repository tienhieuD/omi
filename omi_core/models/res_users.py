# -*- coding: utf-8 -*-
from odoo import api, fields, models

import base64
import requests

class ResPartner(models.Model):
    _inherit = 'res.partner'

    psid = fields.Char("Facebook Page Sender ID")
    page_id = fields.Char("Facebook Page ID")

    def get_as_base64(self, url):
        return base64.b64encode(requests.get(url).content)

    @api.model
    def get_create_partner_from_psid(self, psid, page_id):
        """ Từ sender page id truyền vào, tìm ra người dùng xem đã có trên hệ thống hay chưa?
            Không có thì tạo mới...
        """
        partner = self.search([('psid', '=', psid), ('page_id', '=', page_id)], limit=1)
        print("Search partner: %s" % partner)
        if partner: return partner

        FacebookUtils = self.env['omi.facebook.utils']
        user_info = FacebookUtils.get_sender_info(page_id=page_id, sender_id=psid)
        user_name = user_info['first_name'] + ' ' + user_info['last_name']
        image = self.get_as_base64(user_info['profile_pic'])
        partner = self.create({'name': user_name, 'psid': psid, 'page_id': page_id, 'image': image})
        return partner

