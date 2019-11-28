from odoo import fields, models


class DependenceOrder(models.Model):

    _name = 'tmc.dependence_order'
    _order = 'code'

    name = fields.Char(related='dependence_id.name', readonly=True)

    code = fields.Char(size=7, required=True)

    dependence_id = fields.Many2one(comodel_name='tmc.dependence',
                                    required=True)

    in_actual_nomenclator = fields.Boolean(
        related='dependence_id.in_actual_nomenclator')

    abbreviation = fields.Char(related='dependence_id.abbreviation',
                               readonly=True)

    parent_id = fields.Many2one(comodel_name='tmc.dependence')

    parent_name = fields.Char(related='parent_id.name', readonly=True)

    institutional_classifier_ids = fields.Many2many(
        comodel_name='tmc.institutional_classifier',
        relation='institutional_classifier_dependence_order_rel',
        column1='dependence_order_id',
        column2='institutional_classifier_id',
        readonly=True)
