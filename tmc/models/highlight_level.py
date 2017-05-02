# -*- coding: utf-8 -*-

from odoo import models, fields, _


class Highlight_Level(models.Model):

    _name = 'tmc.highlight_level'

    name = fields.Char(
        required=True
    )

    color = fields.Char(
        string="Color",
        required=True
    )

    details = fields.Text()

    priority = fields.Integer(
        size=2,
        required=True
    )

    _sql_constraints = [
        ('name_unique',
            'UNIQUE(name)',
            _('Highlight Level already exists')),
        ('priority_unique',
            'UNIQUE(priority)',
            _('Priority must be unique'))
    ]
