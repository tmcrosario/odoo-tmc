# -*- coding: utf-8 -*-

from odoo import models, fields


class DocumentRes(models.Model):
    _name = 'tmc.document_res'

    document_id = fields.Many2one(
        comodel_name='tmc.document',
        domain=[('document_type_id.abbreviation', '=', 'RES')],
        string='Document Name',
        required=True,
        ondelete='cascade',
        delegate=True
    )
