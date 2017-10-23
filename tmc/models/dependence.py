# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class Dependence(models.Model):
    _name = 'tmc.dependence'

    name = fields.Char()

    abbreviation = fields.Char(
        size=6
    )

    document_type_ids = fields.Many2many(
        comodel_name='tmc.document_type'
    )

    document_topic_ids = fields.Many2many(
        comodel_name='tmc.document_topic'
    )

    system_ids = fields.Many2many(
        comodel_name='tmc.system'
    )

    in_actual_nomenclator = fields.Boolean()

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if not args:
            args = []
        if self._context.get('search_default_filter_actual_nomenclator'):
            args.extend([('in_actual_nomenclator', '=', True)])
        return super(Dependence, self).name_search(
            name=name,
            args=args,
            operator=operator,
            limit=limit)

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         _('Dependence name must be unique')),

        ('abbreviation_unique',
         'UNIQUE(abbreviation)',
         _('Dependence abbreviation must be unique'))
    ]
