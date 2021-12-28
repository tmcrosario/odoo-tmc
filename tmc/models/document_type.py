from odoo import _, fields, models


class DocumentType(models.Model):

    _name = "tmc.document_type"
    _description = "Document Type"

    name = fields.Char(string="Document Type")

    abbreviation = fields.Char(required=True)

    model = fields.Char(required=True)

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
