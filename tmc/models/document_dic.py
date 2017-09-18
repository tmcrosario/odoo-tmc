# -*- coding: utf-8 -*-

from odoo import models, fields


class DocumentDic(models.Model):
    _name = 'tmc.document_dic'

    document_id = fields.Many2one(
        comodel_name='tmc.document',
        domain=[('document_type_id.abbreviation', '=', 'DIC')],
        string='Document Name',
        required=True,
        ondelete='cascade',
        delegate=True
    )
