# -*- coding: utf-8 -*-

from odoo import models, fields


class DocumentExt(models.Model):
    _name = 'tmc.document_ext'

    document_id = fields.Many2one(
        comodel_name='tmc.document',
        domain=[('document_type_id.abbreviation', '=', 'EXT')],
        string='Document Name',
        required=True,
        ondelete='cascade',
        delegate=True
    )
