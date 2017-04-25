# -*- coding: utf-8 -*-

{
    'name': "TMC Base",
    'summary': 'Main TMC models and functionality',
    'version': '10.0.1.0.0',
    'website': 'https://www.tmcrosario.gob.ar',
    'author': 'Tribunal Municipal de Cuentas - Municipalidad de Rosario',
    'license': 'AGPL-3',
    'depends': [],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/highlight.xml',
        'views/highlight_level.xml',
        'views/document.xml',
        'views/document_type.xml',
        'views/dependence.xml',
        'views/institutional_classifier.xml',
        'views/document_topic.xml',
        'views/document_exp.xml',
        'views/document_ext.xml',
        'views/document_res.xml',
        'views/document_leg.xml',
        'views/document_dec.xml',
        'views/document_dic.xml',
        'views/menu.xml',
        'data/institutional_classifier.xml'
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'qweb': [],
}
