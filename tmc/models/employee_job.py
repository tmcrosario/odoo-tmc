from odoo import fields, models


class EmployeeJob(models.Model):

    _name = 'tmc.hr.employee_job'

    name = fields.Char()

    office_id = fields.Many2one(
        comodel_name='tmc.hr.office'
    )
