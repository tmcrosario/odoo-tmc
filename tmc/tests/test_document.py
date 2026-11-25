from odoo.exceptions import UserError
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

    def test_entry_date_without_raa_access(self):
        # A GD reader without RAA groups (e.g. a JUNCO user) must get the entry
        # date instead of an AccessError on every document list
        if "raa.registry_aa" not in self.env:
            self.skipTest("raa is not installed")
        dependence = self.env["tmc.dependence"].search(
            [("abbreviation", "=", "DEM")], limit=1
        )
        document_type = self.env["tmc.document_type"].search(
            [("abbreviation", "=", "DEC")], limit=1
        )
        registered, plain = self.env["tmc.document"].create(
            [
                {
                    "dependence_id": dependence.id,
                    "document_type_id": document_type.id,
                    "number": 333,
                    "period": "2020",
                },
                {
                    "dependence_id": dependence.id,
                    "document_type_id": document_type.id,
                    "number": 334,
                    "period": "2020",
                },
            ]
        )
        self.env["raa.registry_aa"].create(
            {"document_id": registered.id, "entry_date": "2020-03-15"}
        )
        user = self.env["res.users"].create(
            {
                "name": "GD reader",
                "login": "gd_reader_entry_date",
                "group_ids": [
                    (
                        6,
                        0,
                        [
                            self.env.ref("base.group_user").id,
                            self.env.ref("tmc.group_read_only").id,
                        ],
                    )
                ],
            }
        )
        self.assertFalse(self.env["raa.registry_aa"].with_user(user).has_access("read"))
        docs = (registered | plain).with_user(user)
        docs.invalidate_recordset(["entry_date"])
        values = {d["id"]: d["entry_date"] for d in docs.read(["entry_date"])}
        self.assertEqual(str(values[registered.id]), "2020-03-15")
        self.assertEqual(values[plain.id], plain.create_date.date())

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

    def test_reference_document_missing_model_class(self):
        # JUN declares a model with no class: the compute must not raise
        dependence = self.env["tmc.dependence"].search(
            [("abbreviation", "=", "TMC")], limit=1
        )
        document_type = self.env["tmc.document_type"].search(
            [("abbreviation", "=", "JUN")], limit=1
        )
        self.assertTrue(
            dependence and document_type,
            "TMC dependence and JUN type expected (from tmc_data)",
        )
        self.assertEqual(document_type.model, "document_jun")
        doc = self.env["tmc.document"].create(
            {
                "dependence_id": dependence.id,
                "document_type_id": document_type.id,
                "number": 3,
                "period": "2026",
            }
        )
        self.assertFalse(doc.reference_document)

    def _related_documents(self, count):
        dependence = self.env["tmc.dependence"].search(
            [("abbreviation", "=", "DEM")], limit=1
        )
        document_type = self.env["tmc.document_type"].search(
            [("abbreviation", "=", "DEC")], limit=1
        )
        return self.env["tmc.document"].create(
            [
                {
                    "dependence_id": dependence.id,
                    "document_type_id": document_type.id,
                    "number": 111 + index,
                    "period": "2020",
                }
                for index in range(count)
            ]
        )

    def test_related_documents_symmetric_incremental(self):
        # The web client sends (4, id) and (3, id) on save, not only (6, 0, ids)
        a, b = self._related_documents(2)
        a.write({"related_document_ids": [(4, b.id)]})
        self.assertIn(b, a.related_document_ids)
        self.assertIn(a, b.related_document_ids)
        a.write({"related_document_ids": [(3, b.id)]})
        self.assertNotIn(b, a.related_document_ids)
        self.assertNotIn(a, b.related_document_ids)
        a.write({"related_document_ids": [(6, 0, [b.id])]})
        self.assertIn(a, b.related_document_ids)

    def test_related_documents_symmetric_clear(self):
        a, b, c = self._related_documents(3)
        a.write({"related_document_ids": [(6, 0, [b.id, c.id])]})
        self.assertIn(a, b.related_document_ids | c.related_document_ids)
        a.write({"related_document_ids": [(6, 0, [])]})
        self.assertFalse(a.related_document_ids)
        self.assertNotIn(a, b.related_document_ids | c.related_document_ids)
        a.write({"related_document_ids": [(4, b.id), (4, c.id)]})
        a.write({"related_document_ids": [(5, 0, 0)]})
        self.assertFalse(a.related_document_ids)
        self.assertNotIn(a, b.related_document_ids | c.related_document_ids)

    def test_related_documents_symmetric_multiple_records(self):
        a, b, c = self._related_documents(3)
        (a | b).write({"related_document_ids": [(4, c.id)]})
        self.assertEqual(c.related_document_ids, a | b)
        (a | b).write({"related_document_ids": [(3, c.id)]})
        self.assertFalse(c.related_document_ids)

    def test_related_documents_symmetric_delete_command(self):
        a, b = self._related_documents(2)
        a.write({"related_document_ids": [(4, b.id)]})
        # (2, id) deletes the related document: the sync must not read it
        a.write({"related_document_ids": [(2, b.id)]})
        self.assertFalse(a.related_document_ids)
        self.assertFalse(b.exists())

    def _document_type(self, abbreviation, name):
        # NTA and NJC come from tmc_data; create them when only tmc is installed
        DocumentType = self.env["tmc.document_type"]
        return DocumentType.search(
            [("abbreviation", "=", abbreviation)], limit=1
        ) or DocumentType.create({"abbreviation": abbreviation, "name": name})

    def test_nta_and_njc_numbers_go_beyond_6000(self):
        dependence = self.env["tmc.dependence"].search(
            [("abbreviation", "=", "DEM")], limit=1
        )
        for abbreviation, name in (
            ("NTA", "Nota"),
            ("NJC", "Nota de Junta de Compras"),
        ):
            document = self.env["tmc.document"].create(
                {
                    "dependence_id": dependence.id,
                    "document_type_id": self._document_type(abbreviation, name).id,
                    "number": 123456,
                    "period": "2026",
                }
            )
            self.assertEqual(document.number, 123456, abbreviation)

    def test_other_types_keep_the_6000_limit(self):
        dependence = self.env["tmc.dependence"].search(
            [("abbreviation", "=", "DEM")], limit=1
        )
        document_type = self.env["tmc.document_type"].search(
            [("abbreviation", "=", "DEC")], limit=1
        )
        with self.assertRaises(UserError):
            self.env["tmc.document"].create(
                {
                    "dependence_id": dependence.id,
                    "document_type_id": document_type.id,
                    "number": 6001,
                    "period": "2026",
                }
            )
