from odoo import _, api, fields, models


class Highlight(models.Model):
    _name = "tmc.highlight"
    _description = "Highlight"

    comment = fields.Text(required=True)

    document_id = fields.Many2one(comodel_name="tmc.document")

    @api.model
    def _get_level_selection(self):
        return [
            ("high", _("High")),
            ("medium", _("Medium")),
            ("low", _("Low")),
        ]

    level = fields.Selection(
        selection="_get_level_selection",
        required=True,
    )

    applicable = fields.Boolean(default=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("level"):
                vals["level"] = "low"
        return super().create(vals_list)
