# -*- coding: utf-8 -*-

from odoo import models, fields


class DocumentOrd(models.Model):
    _name = 'tmc.document_ord'

    document_id = fields.Many2one(
        comodel_name='tmc.document',
        domain=[('document_type_id.abbreviation', '=', 'ORD')],
        string='Document Name',
        required=True,
        ondelete='cascade',
        delegate=True
    )
