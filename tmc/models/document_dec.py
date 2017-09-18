# -*- coding: utf-8 -*-

from odoo import models, fields


class DocumentDec(models.Model):
    _name = 'tmc.document_dec'

    document_id = fields.Many2one(
        comodel_name='tmc.document',
        domain=[('document_type_id.abbreviation', '=', 'DEC')],
        string='Document Name',
        required=True,
        ondelete='cascade',
        delegate=True
    )
