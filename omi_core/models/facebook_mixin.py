from odoo import api, models, exceptions

import logging
_logger = logging.getLogger(__name__)

try:
    import facebook
    from pymessenger.bot import Bot
except ImportError as err:
    _logger.debug(err)


class FacebookUtils(models.AbstractModel):
    _name = 'omi.facebook.utils'

    version = 3.1

    @api.model
    def _get_access_token(self):
        return self.env['ir.config_parameter'].sudo().get_param('omi.fb_access_token')

    def _get_page_access_token(self, page_id):
        """
        Get page access token to do page's manipulation.
        :param page_id: ID of Facebook Page
        :return: string: access token
        """
        page_access_token = self.env['omi.fb.page'].search([('page_id', '=', page_id)], limit=1).access_token
        try:
            facebook.GraphAPI(access_token=page_access_token, version=self.version).get_object("me")
            return page_access_token

        except facebook.GraphAPIError as exc:
            _logger.info("Maybe page(%s) access token is expired.\n%s" % (page_id, exc))
            access_token = self._get_access_token()
            try:
                graph = facebook.GraphAPI(access_token=access_token, version=self.version)
                accounts_data = graph.get_connections('me', 'accounts')
                for page in accounts_data['data']:
                    page_token = self.env['omi.fb.page'].search([('page_id', '=', page['id'])], limit=1)

                    if page_token:
                        page_token.write({'access_token': page['access_token']})
                    else:
                        self.env['omi.fb.page'].create({
                            'page_id': page['id'],
                            'access_token': page['access_token'],
                            'name': page['name'],
                        })

                return self._get_page_access_token(page_id)
            except facebook.GraphAPIError as exc:
                _logger.info("Maybe user's access token is expired.\n%s" % exc)
                raise exceptions.MissingError("User access token is expired.\n%s" % exc)

    def get_sender_info(self, page_id, sender_id):
        """
        Get sender info, sender is who interactive with page (comment on a post, send message).
        :param page_id: page ID which sender belong to
        :param sender_id: PSID which is id of Facebook User associated with Page
        :return: dictionary contain info of sender
        """
        page_access_token = self._get_page_access_token(page_id)
        graph_page = facebook.GraphAPI(access_token=page_access_token, version=self.version)
        return graph_page.get_object(id=sender_id)

    def send_message(self, partner, text):
        """
        Send message to user.
        :param partner: res.partner record
        :param text: the message content
        :return: True if send message success
        """
        recipient_id = partner.psid
        page_id = partner.page_id
        if not page_id and not recipient_id:
            exceptions.MissingError("Can't send message to this partner.")
        access_token = self._get_page_access_token(page_id)
        response = Bot(access_token).send_text_message(recipient_id, text)
        if response.get('error'):
            raise exceptions.MissingError("Can't send message to Partner(%s).\n%s" % (response['error'], recipient_id))
        return True
