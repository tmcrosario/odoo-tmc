# -*- coding: utf-8 -*-

from odoo import models, fields


class DocumentLeg(models.Model):
    _name = 'tmc.document_leg'

    document_id = fields.Many2one(
        comodel_name='tmc.document',
        domain=[('document_type_id.abbreviation', '=', 'LEG')],
        string='Document Name',
        required=True,
        ondelete='cascade',
        delegate=True
    )
