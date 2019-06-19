import base64
import requests

from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    psid = fields.Char("Facebook Page Sender ID")
    page_id = fields.Char("Facebook Page ID")
    fb_page_id = fields.Many2one('omi.fb.page', 'Page Name', compute='_compute_facebook_page')
    point = fields.Float('Điểm khách hàng', track_visibility='always')
    rank_id = fields.Many2one('partner.rank', string="Hạng", compute='_compute_rank')
    birth_day = fields.Date('Ngày sinh')
    banned = fields.Boolean(default=False)

    @api.depends('point')
    def _compute_rank(self):
        for rec in self:
            rec.rank_id = self.env['partner.rank'].get_rank(rec.point)

    @api.multi
    def add_point(self, point):
        for rec in self:
            new_point = rec.point + point
            rec.write({'point': new_point})
        return True

    @api.multi
    def sub_point(self, point):
        for rec in self:
            new_point = rec.point - point
            rec.write({'point': new_point})
        return True

    @api.depends('page_id')
    def _compute_facebook_page(self):
        OmiFbPage = self.env['omi.fb.page']
        for partner in self:
            partner.fb_page_id = OmiFbPage.search([('page_id', '=', partner.page_id)], limit=1).id

    @api.model
    def action_show_partner(self, channel_id):
        if not isinstance(channel_id, int):
            return {}
        partner_id = self.env['mail.channel'].browse(channel_id).get_partners().filtered('psid')[:1].id
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [[False, 'form']],
            'res_model': 'res.partner',
            'res_id': partner_id,
            'target': 'new',
        }

    def get_as_base64(self, url):
        return base64.b64encode(requests.get(url).content)

    @api.model
    def get_partner_from_psid(self, psid, page_id, force_create=True):
        """ Từ sender page id truyền vào, tìm ra người dùng xem đã có trên hệ thống hay chưa?
            Không có thì tạo mới...
        """
        partner = self.search([('psid', '=', psid), ('page_id', '=', page_id)], limit=1)

        if not partner and force_create:
            FacebookUtils = self.env['omi.facebook.utils']
            user_info = FacebookUtils.get_sender_info(page_id=page_id, sender_id=psid)
            user_name = user_info['first_name'] + ' ' + user_info['last_name']
            image = self.get_as_base64(user_info['profile_pic'])

            partner = self.create({
                'name': user_name,
                'psid': psid,
                'page_id': page_id,
                'image': image
            })

            _logger.info(
                "Search partner psid(%s) and page_id(%s) with no result, created partner %s(%s)",
                psid, page_id, user_name, partner.id
            )

        return partner

    @api.multi
    def open_point_form(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'point.form',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref('omi_core.point_form').id,
            'target': 'new',
            'context': {'default_partner_id': self.id},
        }


class PartnerRank(models.Model):
    _name = 'partner.rank'
    _description = 'Partner ranks'

    name = fields.Char()
    point_start = fields.Float()
    point_end = fields.Float()

    @api.model
    def get_rank(self, point):
        return self.search([('point_start', '<', point), ('point_end', '>', point)], limit=1).id
