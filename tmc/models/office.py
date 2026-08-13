from odoo import api, fields, models


class Office(models.Model):
    _name = "tmc.hr.office"
    _description = "Office"
    _inherit = "tmc.category"

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

    @api.depends("name", "abbreviation")
    def _compute_display_name(self):
        # MIG(19.0): name_get was removed in 17.0. Office overrides the inherited
        # tmc.category hierarchical display with its own "<name> - <abbreviation>".
        for office in self:
            office.display_name = f"{office.name} - {office.abbreviation}"
