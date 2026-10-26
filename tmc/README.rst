========
TMC Base
========

Sistema de gestión documental del Tribunal Municipal de Cuentas de Rosario.

Módulo principal: administración, seguimiento y organización de documentos.

Funcionalidades
===============

* Seguimiento de documentos por período
* Clasificación jerárquica por temas (principal y secundario)
* Gestión de dependencias municipales
* Clasificador institucional (nomenclador)
* Resaltados y priorización de documentos
* Asistente de edición masiva de temas

Modelos principales
===================

* ``tmc.document``: documento, con período, tipo, temas y resaltados
* ``tmc.dependence``: unidades organizativas y tipos de documento permitidos
* ``tmc.document_topic``: clasificación jerárquica por temas
* ``tmc.institutional_classifier``: nomenclador institucional por período
* ``tmc.document_type``: tipos de documento
* ``tmc.employee``: empleados
* ``tmc.office``: oficinas
* ``tmc.highlight``: prioridades de los documentos

Créditos
========

* Tribunal Municipal de Cuentas - Municipalidad de Rosario

Licencia
========

AGPL-3
