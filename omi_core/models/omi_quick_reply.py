from odoo import fields, models


class OmiQuickReply(models.Model):
    _name = 'omi.quick.reply'

    name = fields.Char()
    sequence = fields.Integer()
    keyword_ids = fields.Many2many('omi.quick.reply.tag')
    reply_content = fields.Text()
    user_id = fields.Many2one('res.users', 'Belong to User')


class OmiQuickReplyTag(models.Model):
    _name = 'omi.quick.reply.tag'

    name = fields.Char()
    color = fields.Integer()
