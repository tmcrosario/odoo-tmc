# -*- coding: utf-8 -*-

from odoo import api, fields, models


class document_topic(models.Model):

    _name = 'tmc.document_topic'
    _description = 'document_topic'
    _inherit = 'tmc.category'

    first_parent_id = fields.Many2one(
        'tmc.document_topic',
        compute='_get_first_parent',
        string='First Parent',
        store=True
    )

    document_ids = fields.Many2many(
        'tmc.document',
        'main_purpose_ids',
        'document_main_purpose_rel',
        string='Document'
    )

    parent_id = fields.Many2one(
        'tmc.document_topic',
        string='Main Purpose'
    )

    child_ids = fields.One2many(
        'tmc.document_topic',
        'parent_id',
        string='Childs'
    )

    important = fields.Boolean()

    @api.one
    @api.depends('parent_id', 'parent_id.parent_id')
    def _get_first_parent(self):
        first_parent_id = False
        parent = self.parent_id
        while parent:
            first_parent_id = parent.id
            parent = parent.parent_id
        self.first_parent_id = first_parent_id
