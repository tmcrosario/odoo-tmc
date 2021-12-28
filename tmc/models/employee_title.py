from odoo import fields, models


class EmployeeTitle(models.Model):

    _name = "tmc.hr.employee_title"
    _description = "Employee Title"

    name = fields.Char()
