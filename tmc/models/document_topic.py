# -*- coding: utf-8 -*-

from odoo import api, fields, models


class document_topic(models.Model):

    _name = 'tmc.document_topic'
    _description = 'document_topic'
    _inherit = 'tmc.category'

    first_parent_id = fields.Many2one(
        comodel_name='tmc.document_topic',
        compute='_get_first_parent',
        store=True
    )

    document_ids = fields.Many2many(
        comodel_name='tmc.document',
        relation='document_main_topic_rel',
        column1='main_topic_ids'
    )

    parent_id = fields.Many2one(
        comodel_name='tmc.document_topic',
        string='Main Topic'
    )

    child_ids = fields.One2many(
        comodel_name='tmc.document_topic',
        inverse_name='parent_id'
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
