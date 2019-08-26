
from odoo import fields, models


class Employee(models.Model):

    _name = 'tmc.hr.employee'
    _order = 'name'

    name = fields.Char()

    internal_number = fields.Char(
        size=3
    )

    docket_number = fields.Integer()

    bank_account_number = fields.Char()

    bank_branch = fields.Integer(
        size=2
    )

    admission_date = fields.Date()

    email = fields.Char()

    active = fields.Boolean(
        default=True
    )

    employee_title_ids = fields.Many2many(
        comodel_name='tmc.hr.employee_title'
    )

    employee_job_id = fields.Many2one(
        comodel_name='tmc.hr.employee_job'
    )

    office_id = fields.Many2one(
        comodel_name='tmc.hr.office'
    )

    _sql_constraints = [
        ('number_uniq',
         'unique(docket_number, bank_account_number)',
         'Number must be unique!'),
    ]
