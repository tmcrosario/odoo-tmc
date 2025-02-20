from odoo import _, api, fields, models


class DocumentType(models.Model):

    _name = "tmc.document_type"
    _description = "Document Type"
    _translate = True

    name = fields.Char(required=True, translate=True)

    abbreviation = fields.Char(required=True)

    model = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('abbreviation'):
                vals['abbreviation'] = vals['abbreviation'].upper()
        return super().create(vals_list)

    _sql_constraints = [
        (
            "name_unique",
            "UNIQUE(name)",
            _("Document type name must be unique"),
        ),
        (
            "abbreviation_unique",
            "UNIQUE(abbreviation)",
            _("Document type abbreviation must be unique"),
        ),
    ]
