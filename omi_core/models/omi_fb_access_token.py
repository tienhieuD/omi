from odoo import fields, models


class OmiFbAccessToken(models.Model):
    _name = 'omi.fb.access.token'

    page_id = fields.Char(required=True)
    access_token = fields.Char(required=True)
