# -*- coding: utf-8 -*-
import facebook
from odoo import api, fields, models, tools


class FacebookUtils(models.AbstractModel):
    _name = 'omi.facebook.utils'

    @api.model
    def _get_access_token(self):
        return self.env['ir.config_parameter'].sudo().get_params('omi.fb_access_token')

    def _get_page_access_token(self, access_token, page_id):
        graph = facebook.GraphAPI(access_token=access_token, version=3.1)
        accounts_data = graph.get_connections('me', 'accounts')
        for page in accounts_data['data']:
            if page['id'] == page_id:
                return page['access_token']

    def get_sender_info(self, page_id, sender_id):
        access_token = self._get_access_token()
        page_access_token = self._get_page_access_token(access_token=access_token, page_id=page_id)
        graph_page = facebook.GraphAPI(access_token=page_access_token, version=3.1)
        return graph_page.get_object(id=sender_id)
