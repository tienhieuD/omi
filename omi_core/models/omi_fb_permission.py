from odoo import api, fields, models


class OmiFbPermission(models.Model):
    _name = 'omi.fb.permission'

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True)

    @api.multi
    def name_get(self):
        return [(perm.id, '%s (%s)' % (perm.name, perm.code)) for perm in self]
