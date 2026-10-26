# Odoo TMC

![Odoo 19.0](https://img.shields.io/badge/Odoo-19.0-714B67)
[![Licencia: AGPL-3](https://img.shields.io/badge/licencia-AGPL--3-blue.svg)](LICENSE)

Sistema de gestión documental del Tribunal Municipal de Cuentas de Rosario.

## Módulos

| Módulo        | Versión    | Descripción                          |
| ------------- | ---------- | ------------------------------------ |
| [`tmc`](tmc/) | 19.0.1.1.0 | Modelos y funcionalidad base del TMC |

## Funcionalidades

- Seguimiento de documentos por período.
- Clasificación jerárquica por temas.
- Gestión de dependencias municipales.
- Clasificador institucional (nomenclador).
- Resaltados y priorización de documentos.

## Instalación

Dependencias OCA: [`web`](https://github.com/OCA/web) (`web_tree_many2one_clickable`), [`server-brand`](https://github.com/OCA/server-brand) (`remove_odoo_enterprise`).

Agregar a la ruta de addons, actualizar aplicaciones e instalar «TMC Base».

## Licencia

[AGPL-3](LICENSE). Autor: Tribunal Municipal de Cuentas - Municipalidad de Rosario (<https://www.tmcrosario.gob.ar>).
