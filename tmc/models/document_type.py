# -*- coding: utf-8 -*-

from odoo import models, fields, _


class Document_Type(models.Model):

    _name = 'tmc.document_type'

    name = fields.Char(
        string='Document Type'
    )

    abbreviation = fields.Char(
        size=3,
        required=True
    )

    model = fields.Char(
        required=True
    )

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         _('Document type name must be unique')),
        ('abbreviation_unique',
         'UNIQUE(abbreviation)',
         _('Document type abbreviation must be unique'))
    ]
