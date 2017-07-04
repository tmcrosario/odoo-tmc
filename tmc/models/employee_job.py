# -*- coding: utf-8 -*-

from odoo import fields, models


class Employee_Job(models.Model):

    _name = 'tmc.hr.employee_job'

    name = fields.Char()

    office_id = fields.Many2one(
        comodel='tmc.hr.office'
    )
