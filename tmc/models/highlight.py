from odoo import _, api, fields, models


class Highlight(models.Model):

    _name = "tmc.highlight"
    _description = "Highlight"
    _translate = True

    comment = fields.Text(required=True)

    document_id = fields.Many2one(comodel_name="tmc.document")

    level = fields.Selection(
        selection=[
            ("high", _("High")),
            ("medium", _("Medium")),
            ("low", _("Low")),
        ],
        required=True,
    )

    applicable = fields.Boolean(default=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("level"):
                vals["level"] = "low"
        return super().create(vals_list)
