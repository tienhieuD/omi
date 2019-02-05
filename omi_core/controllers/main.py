# -*- coding: utf-8 -*-
import json
from datetime import datetime

from odoo import http
from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.addons.auth_oauth.controllers.main import fragment_to_query_string

ACCESS_TOKEN = '1234567890qwertyuiopasdfghjklzxcvbnm'
VERIFY_TOKEN = '1234567890qwertyuiopasdfghjklzxcvbnm'


class OMICore(http.Controller):
    @http.route('/config-save-token', type='http', auth="user", website=True)
    @fragment_to_query_string
    def config_save_token(self, access_token=False, **kwargs):
        request.env['ir.config_parameter'].sudo().set_param('omi.fb_access_token', access_token)
        redirect_menu = request.env.ref('omi_core.menu_omi_config_settings')
        return request.redirect('/web#menu_id=%s' % redirect_menu.id)

    @http.route('/messenger-hook', type='json', methods=['GET', 'POST'], auth="none")
    def messenger_hook(self, **kwargs):
        if request.httprequest.method == 'GET':
            challenge = kwargs.get('hub.challenge')
            mode = kwargs.get('hub.mode')
            token = kwargs.get('hub.verify_token')
            if mode and token:
                if mode == 'subscribe' and token == VERIFY_TOKEN:
                    return challenge
                return 'Invalid verification token'
        else:
            # https://www.twilio.com/blog/2017/12/facebook-messenger-bot-python.html
            post_data = json.loads(request.httprequest.data)
            for event in post_data['entry']:
                messaging = event['messaging']
                for message in messaging:
                    if message.get('message'):
                        # Facebook Messenger ID for user so we know where to send response back to
                        recipient_id = message['sender']['id']
                        if message['message'].get('text'):
                            print(message['message'].get('text'))
                        # if user sends us a GIF, photo, video, or any other non-text item
                        if message['message'].get('attachments'):
                            print(message['message'].get('attachments'))
            return "Message Processed"

