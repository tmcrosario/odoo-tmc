from odoo import fields, models


class Office(models.Model):

    _name = "tmc.hr.office"
    _description = "Office"
    _inherit = "tmc.category"
    _translate = True

    parent_id = fields.Many2one(comodel_name="tmc.hr.office", string="Superior")

    child_ids = fields.One2many(comodel_name="tmc.hr.office", inverse_name="parent_id")

    employee_ids = fields.One2many(
        comodel_name="tmc.hr.employee", inverse_name="office_id"
    )

    manager_id = fields.Many2one(comodel_name="tmc.hr.employee")

    abbreviation = fields.Char(required=True, translate=True)

    employee_job_ids = fields.One2many(
        comodel_name="tmc.hr.employee_job", inverse_name="office_id"
    )

    name = fields.Char(required=True, translate=True)

    def name_get(self):
        result = []
        for office in self:
            result.append((office.id, office.name + " - %s" % office.abbreviation))
        return result
