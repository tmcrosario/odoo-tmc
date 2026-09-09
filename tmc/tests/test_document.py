from odoo.tests import common, tagged


@tagged('post_install', '-at_install')
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

    def test_reference_document_missing_model_class(self):
        """Regression: a document_type whose `model` points to a class that is
        not registered (JUN -> tmc.document_jun, which has no class) must NOT
        raise KeyError when the reference_document compute runs; it stays empty.
        Guards the JUN document used by JUNCO for the Junta de Compras."""
        dependence = self.env["tmc.dependence"].search(
            [("abbreviation", "=", "TMC")], limit=1)
        document_type = self.env["tmc.document_type"].search(
            [("abbreviation", "=", "JUN")], limit=1)
        self.assertTrue(dependence and document_type,
                        "TMC dependence and JUN type expected (from tmc_data)")
        self.assertEqual(document_type.model, "document_jun")
        doc = self.env["tmc.document"].create({
            "dependence_id": dependence.id,
            "document_type_id": document_type.id,
            "number": 3,
            "period": 2026,
        })
        # Accessing the computed field must not raise (KeyError before the guard).
        self.assertFalse(doc.reference_document)
