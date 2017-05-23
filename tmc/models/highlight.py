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

    level = fields.Selection(
        selection=[('high', 'High'),
                   ('medium', 'Medium')]
    )

    applicable = fields.Boolean()
