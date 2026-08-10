from odoo import fields, models


class Category(models.Model):
    _name = "tmc.category"
    _description = "Category"

    name = fields.Char()

    # Non-stored (14.0 behavior): base has no parent_id to depend on; the
    # concrete children (document_topic, hr.office) provide it
    display_name = fields.Char(compute="_compute_display_name")

    def _compute_display_name(self):
        for category in self:
            parent = category.parent_id
            computed_name = category.name
            while parent:
                computed_name = parent.name + " / " + computed_name
                parent = parent.parent_id
            category.display_name = computed_name
