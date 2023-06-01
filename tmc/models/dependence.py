from odoo import _, api, fields, models


class Dependence(models.Model):
    _name = "tmc.dependence"
    _description = "Dependence"

    name = fields.Char()

    abbreviation = fields.Char()

    document_type_ids = fields.Many2many(comodel_name="tmc.document_type")

    document_topic_ids = fields.Many2many(comodel_name="tmc.document_topic")

    document_topic_names = fields.Char(
        string="Document Topics", compute="_compute_document_topic_names"
    )

    system_ids = fields.Many2many(comodel_name="tmc.system")

    in_actual_nomenclator = fields.Boolean()

    @api.depends("document_topic_ids")
    def _compute_document_topic_names(self):
        for record in self:
            record.document_topic_names = ", ".join(
                record.document_topic_ids.mapped("name")
            )

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        if not args:
            args = []
        if self._context.get("search_default_filter_actual_nomenclator"):
            args.extend([("in_actual_nomenclator", "=", True)])
        return super(Dependence, self).name_search(
            name=name, args=args, operator=operator, limit=limit
        )

    _sql_constraints = [
        ("name_unique", "UNIQUE(name)", _("Dependence name must be unique"))
    ]
