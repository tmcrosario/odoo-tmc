# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import Warning


class Institutional_Classifier(models.Model):
    _name = 'tmc.institutional_classifier'
    _rec_name = 'period'
    _order = 'period desc, due_date desc'

    display_name = fields.Char(
        compute='_get_display_name',
        string='Name'
    )

    period = fields.Selection(
        [(num, str(num)) for num in reversed(
            range(((datetime.now().year) - 10), ((datetime.now().year) + 1)))],
        required=True
    )

    due_date = fields.Date()

    dependence_ids = fields.Many2many(
        comodel_name='tmc.dependence',
        relation='institutional_classifier_dependence_rel',
        column1='institutional_classifier_id',
        column2='dependence_id'
    )

    pdf = fields.Binary()

    @api.one
    def _get_display_name(self):
        self.display_name = 'Nomenclador Institucional %s' % str(self.period)
        if not self.due_date:
            self.display_name += ' (Actual)'
        else:
            month = datetime.strptime(self.due_date, "%Y-%m-%d").strftime("%b")
            self.display_name += ' (%s)' % month

    @api.model
    def create(self, values):
        year = datetime.strptime(str(values['period']), '%Y')
        current_nomenclator = self.env['tmc.institutional_classifier'].search([
            ('due_date', '=', False)])
        if year > datetime.today():
            raise Warning(_('Invalid period'))
        if current_nomenclator:
            newest = self.env['tmc.institutional_classifier'].search(
                []
            ).sorted(
                key=lambda r: r.period,
                reverse=True
            )
            if not values['due_date']:
                if newest and values['period'] < newest[0].period:
                    raise Warning(
                        _('There is already a more recent nomenclator'))
                if self.env['tmc.institutional_classifier'].search([
                        ('period', '=', values['period']),
                        ('due_date', '=', False)]):
                    raise Warning(
                        _('Before adding a nomenclator you must set due date \
                            prior to the current'))
        return super(Institutional_Classifier, self).create(values)
