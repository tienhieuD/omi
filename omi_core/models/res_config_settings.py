from odoo import api, fields, models, _
from odoo.exceptions import MissingError

import logging
_logger = logging.getLogger(__name__)

try:
    import facebook
except ImportError as err:
    _logger.debug(err)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    fb_app_id = fields.Char('Facebook App ID')
    fb_permission = fields.Many2many('omi.fb.permission', string='Permissions')
    fb_access_token = fields.Text('Access token')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param

        fb_permission_codes = get_param('omi.fb_permission', '').split(',')
        fb_permissions = self.env['omi.fb.permission'].search([('code', 'in', fb_permission_codes)]).ids or False

        res.update(
            fb_app_id=get_param('omi.fb_app_id'),
            fb_permission=fb_permissions,
            fb_access_token=get_param('omi.fb_access_token'),
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        set_param = self.env['ir.config_parameter'].sudo().set_param

        fb_permission_codes = ",".join(self.fb_permission.mapped('code'))

        set_param('omi.fb_permission', fb_permission_codes)
        set_param('omi.fb_app_id', self.fb_app_id)
        set_param('omi.fb_access_token', self.fb_access_token)

    @api.multi
    def get_facebook_access_token(self):
        self.execute()
        get_param = self.env['ir.config_parameter'].sudo().get_param

        base_url = 'http://localhost'  # get_param('web.base.url', 'http://localhost')
        https_url = base_url.replace("http://", "https://")
        canvas_url = https_url + "/config-save-token"

        perms = get_param('omi.fb_permission', '').split(',')

        app_id = self.fb_app_id

        if app_id and canvas_url and perms:
            graph = facebook.GraphAPI(version=3.1)
            auth_url = "%s&response_type=token" % graph.get_auth_url(app_id, canvas_url, perms)
            return {
                'type': 'ir.actions.act_url',
                'url': auth_url,
                'target': 'self',
                'target_type': 'public',
            }
        raise MissingError(_('Require "Facebook App ID" and "Permissions"'))
