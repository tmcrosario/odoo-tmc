
from odoo import fields, models


class System(models.Model):

    _name = 'tmc.system'

    name = fields.Char()
