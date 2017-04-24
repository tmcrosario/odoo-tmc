# -*- coding: utf-8 -*-

from odoo import models, fields


class Document_Exp(models.Model):
    _name = 'tmc.document_exp'

    document_id = fields.Many2one(
        comodel_name='tmc.document',
        domain=[('document_type_id.abbreviation', '=', 'EXP')],
        string='Document Name',
        required=True,
        ondelete='cascade',
        delegate=True
    )
