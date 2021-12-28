from odoo.tests import common


@common.at_install(False)
@common.post_install(True)
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
