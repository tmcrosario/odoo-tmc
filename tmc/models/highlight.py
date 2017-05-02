# -*- coding: utf-8 -*-

from odoo import models, fields


class Highlight(models.Model):

    _name = 'tmc.highlight'

    comment = fields.Text(
        required=True
    )

    document_id = fields.Many2one(
        comodel_name='tmc.document',
        string='Document'
    )

    highlight_level_id = fields.Many2one(
        comodel_name='tmc.highlight_level',
        string='Highlight Level',
        required=True
    )

    color = fields.Char(
        related='highlight_level_id.color'
    )

    applicable = fields.Boolean()
