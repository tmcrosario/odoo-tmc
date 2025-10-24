========
TMC Base
========

Document Management System for Tribunal Municipal de Cuentas de Rosario.

Main module providing core functionality for document administration, tracking, and organization.

Features
========

* Period-based document tracking
* Hierarchical topic classification (main and secondary)
* Municipal dependencies management
* Institutional classifier (nomenclator)
* Document highlights and prioritization
* Mass topic editing wizard

Main Models
===========

* ``tmc.document`` - Main document model with period, type, topics, and highlights
* ``tmc.dependence`` - Organizational units with allowed document types
* ``tmc.document_topic`` - Hierarchical topic categorization
* ``tmc.institutional_classifier`` - Period-based institutional nomenclator
* ``tmc.document_type`` - Document type definitions
* ``tmc.employee`` - Employee management
* ``tmc.office`` - Office management
* ``tmc.highlight`` - Document priorities

Credits
=======

* Tribunal Municipal de Cuentas - Municipalidad de Rosario

License
=======

AGPL-3
