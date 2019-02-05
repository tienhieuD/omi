# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.addons.auth_oauth.controllers.main import fragment_to_query_string


class OMICore(http.Controller):
    @http.route('/config-save-token', type='http', auth="user", website=True)
    @fragment_to_query_string
    def config_save_token(self, access_token=False, **kwargs):
        request.env['ir.config_parameter'].sudo().set_param('omi.fb_access_token', access_token)
        redirect_menu = request.env.ref('omi_core.menu_omi_config_settings')
        return request.redirect('/web#menu_id=%s' % redirect_menu.id)
