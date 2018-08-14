# -*- coding: utf-8 -*-

{
    'name': "TMC Base",
    'summary': 'Main TMC models and functionality',
    'version': '10.0.1.0.0',
    'website': 'https://www.tmcrosario.gob.ar',
    'author': 'Tribunal Municipal de Cuentas - Municipalidad de Rosario',
    'license': 'AGPL-3',
    'sequence': 150,
    'depends': [
        'web_x2many_delete_all',
        'web_hide_db_manager_link',
        'auditlog',
        'web_favicon',
        'base_optional_quick_create',
        'web_export_view',
        'web_listview_range_select',
        'web_sheet_full_width',
        # 'mass_editing',
        'web_tree_many2one_clickable',
        'base_technical_features',
        'web_search_with_and',
        'report_py3o'
    ],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/highlight.xml',
        'views/document.xml',
        'views/document_type.xml',
        'views/dependence.xml',
        'views/dependence_order.xml',
        'views/institutional_classifier.xml',
        'views/document_topic.xml',
        'views/employee.xml',
        'views/office.xml',
        'views/country_state.xml',
        'report/dependence_document_topics.xml',
        'views/menu.xml'
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'qweb': [],
}
