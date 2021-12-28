from odoo import fields, models


class EmployeeJob(models.Model):

    _name = "tmc.hr.employee_job"
    _description = "Employee Job"

    name = fields.Char()

    office_id = fields.Many2one(comodel_name="tmc.hr.office")
