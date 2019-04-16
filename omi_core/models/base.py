from odoo import api, models


class Base(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        records = super(Base, self).search_read(domain, fields, offset, limit, order)

        x2m_fields = self._context.get('read_x2m_fields')
        if x2m_fields:
            for rec in records:
                for field, option in x2m_fields.items():
                    model = self.fields_get(field, {}).get(field, {}).get('relation')
                    if not model:
                        continue
                    option_limit = option.get('limit')
                    ids = rec[field][:option_limit]
                    option_fields = option.get('fields')
                    rec[field] = self.env[model].browse(ids).read(fields=option_fields)

        return records
