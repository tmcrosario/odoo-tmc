# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class Dependence(models.Model):
    _name = 'tmc.dependence'
    _order = 'code'

    code = fields.Char(
        size=7,
        required=True
    )

    name = fields.Char()

    abbreviation = fields.Char(
        size=4
    )

    parent_id = fields.Many2one(
        'tmc.dependence',
        string='Parent'
    )

    child_ids = fields.One2many(
        'tmc.dependence',
        'parent_id',
        string='Childs'
    )

    document_type_ids = fields.Many2many(
        'tmc.document_type',
        string='Document Types'
    )

    system_ids = fields.Many2many(
        comodel_name='tmc.system',
        string='Systems'
    )

    institutional_classifier_ids = fields.Many2many(
        comodel_name='tmc.institutional_classifier',
        relation='institutional_classifier_dependence_rel',
        column1='dependence_id',
        column2='institutional_classifier_id'
    )

    in_actual_nomenclator = fields.Boolean(
        compute='_get_in_actual_nomenclator',
        store=True
    )

    @api.one
    @api.depends('institutional_classifier_ids')
    def _get_in_actual_nomenclator(self):
        if self.institutional_classifier_ids:
            if self.env['tmc.institutional_classifier'].search([
                ('id', 'in', self.institutional_classifier_ids.mapped('id')),
                    ('due_date', '=', False)], limit=1):
                self.in_actual_nomenclator = True

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
