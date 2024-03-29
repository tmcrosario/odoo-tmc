from odoo import api, fields, models


class Category(models.Model):

    _name = "tmc.category"
    _description = "Category"

    name = fields.Char()

    display_name = fields.Char(compute="_compute_display_name")

    def _compute_display_name(self):
        for category in self:
            parent = category.parent_id
            computed_name = category.name
            while parent:
                computed_name = parent.name + " / " + computed_name
                parent = parent.parent_id
            category.display_name = computed_name

    def name_get(self):
        result = []
        for cat in self:
            prefix = None
            if cat.parent_id:
                prefix = cat.parent_id.name_get()[0][1] + " / "
            result.append((cat.id, "%s %s" % (prefix or "", cat.name)))
        return result
