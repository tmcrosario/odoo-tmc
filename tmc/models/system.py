from odoo import fields, models


class System(models.Model):
    _name = "tmc.system"
    _description = "System"
    _order = "name"

    name = fields.Char(required=True)
    color = fields.Integer()

    _name_unique = models.Constraint("UNIQUE(name)", "System name must be unique")
