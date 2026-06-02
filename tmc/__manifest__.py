{
    "name": "TMC Base",
    "summary": "Main TMC models and functionality",
    "version": "19.0.1.0.0",
    "website": "https://www.tmcrosario.gob.ar",
    "author": "Tribunal Municipal de Cuentas - Municipalidad de Rosario",
    "license": "AGPL-3",
    "sequence": 150,
    "depends": [
        "base",
        # NOTE: tmc references tmc_data records at runtime via env.ref
        # (seq_tmc_act, document topics). This is an intentional RUNTIME coupling,
        # not a manifest dependency: tmc_data depends on tmc, so declaring tmc_data
        # here would create a circular dependency. See MIGRATION_NOTES.md.
        # TODO(19.0 migration): restore "web_tree_many2one_clickable" when available.
        # TODO(19.0 migration): restore "remove_odoo_enterprise" when available.
    ],
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "views/tmc_menus.xml",
        "views/country_state_views.xml",
        "views/country_state_menus.xml",
        "views/dependence_views.xml",
        "views/dependence_menus.xml",
        "views/dependence_order_views.xml",
        "views/document_views.xml",
        "views/document_menus.xml",
        "views/document_topic_views.xml",
        "views/document_topic_menus.xml",
        "views/document_type_views.xml",
        "views/document_type_menus.xml",
        "views/employee_views.xml",
        "views/employee_menus.xml",
        "views/highlight_views.xml",
        "views/institutional_classifier_views.xml",
        "views/institutional_classifier_menus.xml",
        "views/office_views.xml",
        "wizard/mass_edit_document_topics_views.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
}  # yapf: disable
