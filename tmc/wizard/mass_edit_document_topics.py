from odoo import fields, models


class MassEditDocumentTopics(models.TransientModel):
    _name = "tmc.mass_edit_document_topics_wizard"

    dependence_id = fields.Many2one(comodel_name="tmc.dependence", readonly=True)

    document_topic_ids = fields.Many2many(related="dependence_id.document_topic_ids")

    main_topic_ids = fields.Many2many(
        comodel_name="tmc.document_topic",
        relation="mass_edit_document_main_topic_wizard_rel",
        column1="tmc_document_id",
        column2="tmc_document_topic_id",
        domain="[('parent_id', '=', False), ('id', 'in', document_topic_ids)]",
    )

    secondary_topic_ids = fields.Many2many(
        comodel_name="tmc.document_topic",
        relation="mass_edit_document_secondary_topic_wizard_rel",
        domain="[('parent_id', 'in', main_topic_ids)]",
    )

    def save_document_topics(self):
        if self.env.context.get("remove_document_topics"):
            for document in self.env.context.get("active_ids"):
                document_obj = self.env["tmc.document"].browse(document)
                document_obj.main_topic_ids -= self.main_topic_ids
                document_obj.secondary_topic_ids -= self.secondary_topic_ids
        else:
            for document in self.env.context.get("active_ids"):
                document_obj = self.env["tmc.document"].browse(document)
                document_obj.main_topic_ids |= self.main_topic_ids
                document_obj.secondary_topic_ids |= self.secondary_topic_ids
