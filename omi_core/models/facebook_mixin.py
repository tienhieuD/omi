from odoo import api, models

import logging
_logger = logging.getLogger(__name__)

try:
    import facebook
    from pymessenger.bot import Bot
except ImportError as err:
    _logger.debug(err)


class FacebookUtils(models.AbstractModel):
    _name = 'omi.facebook.utils'

    @api.model
    def _get_access_token(self):
        return self.env['ir.config_parameter'].sudo().get_param('omi.fb_access_token')

    def _get_page_access_token(self, page_id):
        access_token = self._get_access_token()
        graph = facebook.GraphAPI(access_token=access_token, version=3.1)
        accounts_data = graph.get_connections('me', 'accounts')
        for page in accounts_data['data']:
            if page['id'] == page_id:
                return page['access_token']

    def get_sender_info(self, page_id, sender_id):
        page_access_token = self._get_page_access_token(page_id)
        graph_page = facebook.GraphAPI(access_token=page_access_token, version=3.1)
        return graph_page.get_object(id=sender_id)

    def send_message(self, partner, text):
        recipient_id = partner.psid
        page_id = partner.page_id
        if page_id and recipient_id:
            access_token = self._get_page_access_token(page_id)
            Bot(access_token).send_text_message(recipient_id, text)
        return True
