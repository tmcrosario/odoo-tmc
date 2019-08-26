
from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import Warning


class InstitutionalClassifier(models.Model):
    _name = 'tmc.institutional_classifier'
    _rec_name = 'period'
    _order = 'period desc, due_date desc'

    display_name = fields.Char(
        compute='_compute_display_name',
        string='Name'
    )

    period = fields.Selection(
        selection=[(num, str(num)) for num in reversed(
            range(((datetime.now().year) - 10), ((datetime.now().year) + 1)))],
        required=True
    )

    due_date = fields.Date()

    dependence_order_ids = fields.Many2many(
        comodel_name='tmc.dependence_order',
        relation='institutional_classifier_dependence_order_rel',
        column1='institutional_classifier_id',
        column2='dependence_order_id'
    )

    pdf = fields.Binary()

    document_id = fields.Many2one(
        comodel_name='tmc.document'
    )

    @api.multi
    def _compute_display_name(self):
        for classifier in self:
            classifier.display_name = _('Year %s') % str(classifier.period)
            if not classifier.due_date:
                classifier.display_name += _(' (Current)')
            else:
                month = datetime.strptime(
                    classifier.due_date, '%Y-%m-%d').strftime('%b')
                classifier.display_name += ' (%s)' % month

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
            if 'due_date' in values:
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
        return super(InstitutionalClassifier, self).create(values)

    @api.multi
    def write(self, vals):
        if not self.due_date and vals.get('dependence_order_ids'):

            dependence_orders = vals['dependence_order_ids'][0][2]
            dependences = self.env['tmc.dependence_order'].search(
                [('id', 'in', dependence_orders)]).mapped('dependence_id')

            self.env['tmc.dependence'].search([]).write(
                {'in_actual_nomenclator': False})
            for dependence in dependences:
                dependence.in_actual_nomenclator = True

        return super(InstitutionalClassifier, self).write(vals)
