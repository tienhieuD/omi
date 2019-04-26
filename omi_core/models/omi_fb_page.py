from odoo import fields, models


class OmiFbAccessToken(models.Model):
    _name = 'omi.fb.page'

    name = fields.Char()
    page_id = fields.Char(required=True)
    access_token = fields.Text(required=True)
