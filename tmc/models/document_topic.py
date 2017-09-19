# -*- coding: utf-8 -*-

from odoo import api, fields, models


class DocumentTopic(models.Model):

    _name = 'tmc.document_topic'
    _description = 'document_topic'
    _inherit = 'tmc.category'

    first_parent_id = fields.Many2one(
        comodel_name='tmc.document_topic',
        compute='_compute_first_parent',
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

    @api.multi
    @api.depends('parent_id',
                 'parent_id.parent_id')
    def _compute_first_parent(self):
        for document_topic in self:
            first_parent_id = False
            parent = document_topic.parent_id
            while parent:
                first_parent_id = parent.id
                parent = parent.parent_id
            document_topic.first_parent_id = first_parent_id
