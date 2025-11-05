from odoo import api, fields, models


class Dependence(models.Model):
    _name = "tmc.dependence"
    _description = "Dependence"
    _translate = True

    name = fields.Char(translate=True)

    abbreviation = fields.Char()

    document_type_ids = fields.Many2many(comodel_name="tmc.document_type")

    document_topic_ids = fields.Many2many(comodel_name="tmc.document_topic")

    document_topic_names = fields.Char(
        string="Document Topics",
        compute="_compute_document_topic_names",
        translate=True,
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
    def name_search(self, name, domain=None, operator="ilike", limit=100):
        if not domain:
            domain = []
        if self.env.context.get("search_default_filter_actual_nomenclator"):
            domain.extend([("in_actual_nomenclator", "=", True)])
        return super().name_search(name=name, domain=domain, operator=operator, limit=limit)

    _name_unique = models.Constraint("UNIQUE(name)", "Dependence name must be unique")
