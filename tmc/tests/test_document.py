from odoo.tests import common, tagged


@tagged("post_install", "-at_install")
class TestDocument(common.TransactionCase):
    def test_create(self):
        Documents = self.env["tmc.document"]

        Dependences = self.env["tmc.dependence"]
        dependence = Dependences.search([("abbreviation", "=", "DEM")])

        Document_Type = self.env["tmc.document_type"]
        document_type = Document_Type.search([("abbreviation", "=", "DEC")])

        Documents.create(
            {
                "dependence_id": dependence.id,
                "document_type_id": document_type.id,
                "number": 4567,
                "period": 2016,
            }
        )

    def test_period_allows_historical_years(self):
        # Migrated documents predate the old rolling window; 1948+ must stay
        # selectable or they fail Selection validation on save
        dependence = self.env["tmc.dependence"].search(
            [("abbreviation", "=", "DEM")], limit=1
        )
        document_type = self.env["tmc.document_type"].search(
            [("abbreviation", "=", "DEC")], limit=1
        )
        document = self.env["tmc.document"].create(
            {
                "dependence_id": dependence.id,
                "document_type_id": document_type.id,
                "number": 1,
                "period": "1950",
            }
        )
        self.assertEqual(document.period, "1950")

    def test_act_name_is_stable_on_recompute(self):
        # An ACT name must use the stored number, not the live sequence, or
        # a later recompute rewrites historical names with today's counter
        dependence = self.env["tmc.dependence"].search(
            [("abbreviation", "=", "DEM")], limit=1
        )
        act_type = self.env["tmc.document_type"].search(
            [("abbreviation", "=", "ACT")], limit=1
        )
        self.assertTrue(act_type, "ACT document type must exist in seed data")

        act = self.env["tmc.document"].create(
            {
                "dependence_id": dependence.id,
                "document_type_id": act_type.id,
                "period": "2020",
            }
        )
        original_prefix = act.name.split("/")[0]
        self.assertIn("ACT-", original_prefix)

        # Advance the shared sequence as if more ACTs had been created
        self.env["ir.sequence"].next_by_code("tmc.document")

        # Force a recompute of the stored name
        act.write({"period": "2021"})

        self.assertEqual(
            act.name.split("/")[0],
            original_prefix,
            "recompute rewrote the ACT number with the live counter",
        )
