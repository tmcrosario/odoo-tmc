{
    'name': "TMC Base Reports",
    'summary': "Odoo reports for TMC using OCA alternative reporting engine",
    'version': '13.0.1.0.1',
    'website': 'https://www.tmcrosario.gob.ar',
    'author': 'Tribunal Municipal de Cuentas - Municipalidad de Rosario',
    'license': 'AGPL-3',
    'sequence': 150,
    'depends': [
        'tmc',
        'report_py3o',
        'report_py3o_fusion_server'
    ],
    'data': [
        'report/dependence_document_topics.xml'
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'qweb': [],
}  # yapf: disable
