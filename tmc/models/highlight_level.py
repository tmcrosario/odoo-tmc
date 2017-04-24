# -*- coding: utf-8 -*-

from odoo import models, fields, _


class Highlight_Level(models.Model):

    _name = 'tmc.highlight_level'

    _colors_ = [
        ('red', 'Red'),
        ('yellow', 'Yellow'),
    ]

    name = fields.Char(
        required=True
    )

    color = fields.Selection(
        selection=_colors_,
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
