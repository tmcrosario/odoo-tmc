# -*- coding: utf-8 -*-

from odoo import fields, models


class Employee_Title(models.Model):

    _name = 'tmc.hr.employee_title'

    name = fields.Char()
