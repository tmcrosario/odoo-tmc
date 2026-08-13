from datetime import datetime

from odoo import api, fields, models
from odoo.exceptions import UserError


class InstitutionalClassifier(models.Model):
    _name = "tmc.institutional_classifier"
    _description = "Institutional Classifier"
    _rec_name = "period"
    _order = "period desc, due_date desc"

    display_name = fields.Char(compute="_compute_display_name", string="Name")

    # Fixed lower bound: a rolling window invalidates seeded records over time
    period = fields.Selection(
        selection=[
            (str(num), str(num))
            for num in reversed(range(2015, datetime.now().year + 1))
        ],
        required=True,
    )

    due_date = fields.Date()

    dependence_order_ids = fields.Many2many(
        comodel_name="tmc.dependence_order",
        relation="institutional_classifier_dependence_order_rel",
        column1="institutional_classifier_id",
        column2="dependence_order_id",
    )

    pdf = fields.Binary()

    document_id = fields.Many2one(comodel_name="tmc.document")

    @api.depends("period", "due_date")
    def _compute_display_name(self):
        for classifier in self:
            classifier.display_name = str(classifier.period)
            if not classifier.due_date:
                classifier.display_name += self.env._(" (Current)")
            else:
                month = classifier.due_date.strftime("%b")
                classifier.display_name += f" ({month})"

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            year = datetime.strptime(str(values["period"]), "%Y")
            current_nomenclator = self.env["tmc.institutional_classifier"].search(
                [("due_date", "=", False)]
            )
            if year > datetime.today():
                raise UserError(self.env._("Invalid period"))
            if current_nomenclator:
                # Full scan intended: find the newest classifier by period
                # pylint: disable=no-search-all
                newest = (
                    self.env["tmc.institutional_classifier"]
                    .search([])
                    .sorted(key=lambda r: r.period, reverse=True)
                )
                if "due_date" in values:
                    if not values["due_date"]:
                        if newest and values["period"] < newest[0].period:
                            raise UserError(
                                self.env._("There is already a more recent nomenclator")
                            )
                        if self.env["tmc.institutional_classifier"].search(
                            [
                                ("period", "=", values["period"]),
                                ("due_date", "=", False),
                            ]
                        ):
                            raise UserError(
                                self.env._(
                                    "Before adding a nomenclator you must set due date prior to the current"
                                )
                            )
        return super().create(vals_list)

    def write(self, vals):
        result = super().write(vals)

        if "dependence_order_ids" in vals:
            for record in self:
                if not record.due_date:
                    # Full scan intended: reset the flag on every dependence
                    # pylint: disable=no-search-all
                    self.env["tmc.dependence"].search([]).write(
                        {"in_actual_nomenclator": False}
                    )
                    for dep_order in record.dependence_order_ids:
                        dep_order.dependence_id.in_actual_nomenclator = True
                    break

        return result
