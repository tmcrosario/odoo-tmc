# -*- coding: utf-8 -*-

from odoo import fields, models


class Dependence_Hierarchy(models.Model):

    _name = 'tmc.dependence_hierarchy'
    _order = 'code'

    name = fields.Char(
        related='dependence_id.name',
        readonly=True
    )

    code = fields.Char(
        size=7,
        required=True
    )

    dependence_id = fields.Many2one(
        comodel_name='tmc.dependence',
        required=True
    )

    abbreviation = fields.Char(
        related='dependence_id.abbreviation',
        readonly=True
    )

    parent_id = fields.Many2one(
        comodel_name='tmc.dependence'
    )

    institutional_classifier_ids = fields.Many2many(
        comodel_name='tmc.institutional_classifier',
        relation='institutional_classifier_dependence_hierarchy_rel',
        column1='dependence_hierarchy_id',
        column2='institutional_classifier_id',
        readonly=True
    )
