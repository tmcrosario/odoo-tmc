# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


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

    shown_in_selection = fields.Boolean(
        string='Shown in Selection'
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

    observations = fields.Text()

    @api.one
    @api.depends('institutional_classifier_ids')
    def _get_in_actual_nomenclator(self):
        if self.institutional_classifier_ids:
            if self.env['tmc.institutional_classifier'].search([
                ('id', 'in', self.institutional_classifier_ids.mapped('id')),
                    ('due_date', '=', False)], limit=1):
                self.in_actual_nomenclator = True

    @api.constrains('shown_in_selection')
    def _check_shown_in_selection(self):
        if not self.abbreviation and self.shown_in_selection:
            raise Warning(
                _('You must set an abbreviation in order to use in system'))

    @api.multi
    @api.onchange('abbreviation')
    def _onchange_abbreviation(self):
        if not self.abbreviation:
            self.shown_in_selection = False

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
