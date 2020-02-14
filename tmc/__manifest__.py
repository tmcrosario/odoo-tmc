{
    'name': "TMC Base",
    'summary': 'Main TMC models and functionality',
    'version': '13.0.1.0.1',
    'website': 'https://www.tmcrosario.gob.ar',
    'author': 'Tribunal Municipal de Cuentas - Municipalidad de Rosario',
    'license': 'AGPL-3',
    'sequence': 150,
    'depends': [
        'report_py3o',
        'report_py3o_fusion_server',
        'web_tree_many2one_clickable',
        # 'web_advanced_search',
        # 'auditlog',
        # 'web_favicon',
        # 'web_export_view',
        # 'web_listview_range_select',
        # 'base_technical_features',
        # 'web_m2x_options',
        # 'web_search_with_and'
    ],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/tmc_menus.xml',
        'views/country_state_views.xml',
        'views/country_state_menus.xml',
        'views/dependence_views.xml',
        'views/dependence_menus.xml',
        'views/dependence_order_views.xml',
        'views/document_views.xml',
        'views/document_menus.xml',
        'views/document_topic_views.xml',
        'views/document_topic_menus.xml',
        'views/document_type_views.xml',
        'views/document_type_menus.xml',
        'views/employee_views.xml',
        'views/employee_menus.xml',
        'views/highlight_views.xml',
        'views/institutional_classifier_views.xml',
        'views/institutional_classifier_menus.xml',
        'views/office_views.xml',
        'report/report_dependence_document_topics.xml'
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'qweb': [],
}  # yapf: disable
