from odoo import fields, models


class System(models.Model):

    _name = "tmc.system"
    _description = "System"

    name = fields.Char()
