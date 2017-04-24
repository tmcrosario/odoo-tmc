# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Category(models.Model):

    _name = 'tmc.category'
    _description = 'category'

    name = fields.Char()

    display_name = fields.Char(
        compute='_get_display_name',
    )

    @api.one
    def _get_display_name(self):
        parent = self.parent_id
        computed_name = self.name
        while parent:
            computed_name = parent.name + ' / ' + computed_name
            parent = parent.parent_id
        self.display_name = computed_name

    @api.multi
    def name_get(self):
        result = []
        for cat in self:
            prefix = None
            if cat.parent_id:
                prefix = cat.parent_id.name_get()[0][1] + ' / '
            result.append((cat.id, "%s %s" % (prefix or '', cat.name)))
        return result
