from odoo import api, fields, models


class Note(models.Model):
    _inherit = 'note.note'

    relate_channel_id = fields.Many2one("mail.channel", "Channel")

    @api.model
    def default_get(self, fields):
        res = super(Note, self).default_get(fields)
        channel_id = self._context.get('channel_to_default')
        if channel_id and isinstance(channel_id, int):
            res['relate_channel_id'] = channel_id
        return res

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        """ Seach note base on chat channel_id """
        channel_id = self._context.get('channel_id_to_domain')
        if channel_id and isinstance(channel_id, int):
            domain += [('relate_channel_id', '=', channel_id)]
        return super(Note, self).search_read(domain, fields, offset, limit, order)
