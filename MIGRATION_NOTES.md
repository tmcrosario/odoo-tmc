# Migration Notes — odoo-tmc (14.0 → 19.0)

Module: `tmc` (TMC Base). This repo had a **pre-existing, partially-migrated `19.0`
branch** (created earlier). Most of the view layer (tree→list, attrs→expressions) and
several model changes were already done there, plus the removal of the old
`bi_reporting` and `tmc_reports` sub-trees. This round **continued on that branch** and
finished the remaining leftovers below. Nothing was harvested from the `18.0` branch
(the `19.0` branch already supersedes it); the `18.0` branch was not used as a base.

## Summary of changes by category

### Models

- **`name_get` removed (17.0):**
  - `tmc/models/category.py` (`tmc.category`): dropped the redundant `name_get`. The
    model already defines `_compute_display_name` producing the same hierarchical
    `"Parent / Child"` string, so the `name_get` was pure duplication. (Clean drop.)
  - `tmc/models/office.py` (`tmc.hr.office`, inherits `tmc.category`): its `name_get`
    produced a **different** string — `"<name> - <abbreviation>"` — not the inherited
    hierarchical one. Dropping it would have silently changed office display names.
    Ported it to an override of `_compute_display_name` with
    `@api.depends("name", "abbreviation")`, preserving the exact
    `"<name> - <abbreviation>"` output.
- **`fields_view_get` removed (16.0):** `tmc/models/document.py` — migrated to an
  `@api.model get_views(self, views, options=None)` override. The original removed the
  add/remove-document-topics **server-action buttons** from the toolbar when
  `disable_document_topics_wizards` is in the context. In 16.0+ the toolbar is assembled
  by `get_views` under `res["views"][view_type]["toolbar"]["action"]`, so the filtering
  was rewritten against that structure (see review flag below).
- **`xmlid_to_res_id` → `self.env.ref(x).id`:** `tmc/models/document.py`
  `show_or_add_content`.
- **Obsolete `"view_type": "form"` key** removed from the `show_or_add_content`
  `act_window` dict.
- **Non-standard `_translate = True`** model attribute removed from 7 models
  (`document.py`, `dependence.py`, `office.py`, `document_topic.py`, `document_type.py`,
  `highlight.py`, `institutional_classifier.py`). Per-field `translate=True` left
  intact.
- `_sql_constraints` left as-is (the repo's CLAUDE.md endorses that style;
  `tmc.document` already uses the modern `models.Constraint` form — left untouched).

### Views

- The pre-existing partial migration had already converted `<tree>`→`<list>`,
  `view_mode` and `attrs` across the view files. The one remaining bug was fixed:
  - `tmc/views/document_views.xml:121`:
    `context="{'tree_view_ref': 'tmc.document_simple_view_tree'}"` →
    `context="{'list_view_ref': 'tmc.document_simple_view_list'}"`. The old ref was
    **dangling** (no record `document_simple_view_tree` exists; the real view is
    `document_simple_view_list`, defined in the same file). Both the context key (17.0
    rename) and the target id were corrected.

### Security

- No `groups_id`/`category_id` changes were required on this round's leftovers
  (security/groups.xml was already touched by the partial migration). Re-grep at
  validation: see review flag.

### Tests

- `tmc/tests/test_document.py`: replaced removed `@common.at_install(False)` /
  `@common.post_install(True)` with `@tagged("post_install", "-at_install")`.

### Manifest

- `version` already `19.0.1.0.0`. License `AGPL-3`.
- **`depends` restored**: was fully commented out. Set to `["base"]`. The two OCA/custom
  modules (`web_tree_many2one_clickable`, `remove_odoo_enterprise`) are kept
  **commented** with `# TODO(19.0 migration)` because their 19.0 availability is
  unverified (offline).
- **`tmc_data` is deliberately NOT added to `depends`** — see Runtime couplings.

## Runtime couplings (important)

`tmc` references `tmc_data` records at runtime via `env.ref` in
`tmc/models/document.py`:

- `tmc_data.seq_tmc_act` (in `_compute_name` and `create`)
- `tmc_data.tmc_document_topic_modifica_presupuesto` (in `write`)
- `tmc_data.tmc_document_topic_periodo` (in `write`)

Meanwhile `tmc_data` depends on `tmc`. This is an **intentional runtime coupling**, not
a manifest dependency: both modules are always installed together, so the refs resolve
at runtime. Declaring `tmc_data` under `tmc`'s `depends` would create a **circular
dependency** that Odoo refuses to install. This bidirectional coupling is a known smell
to revisit later (out of scope here).

## Dormant / dead code (note only, not changed)

- `tmc/models/document.py` `_compute_entry_date` calls
  `self.env["raa.registry_aa"].search(...)`, but the `entry_date` field is commented out
  → the method is effectively dead. No `raa` dependency was added. Future cleanup
  candidate.

## Removed dependencies

- None removed this round. (`bi_reporting` / `tmc_reports` were already removed by the
  partial migration.)

## Dependencies to verify before push

- `web_tree_many2one_clickable` (OCA/web) and `remove_odoo_enterprise` — kept commented;
  verify 19.0 availability and restore if present.

## attrs conversions to review

- None done this round (attrs were already converted on the pre-existing branch).
  Recommend a visual diff review of the earlier attrs conversions at validation.

## Autosave / onchange → constrains conversions

- None required. No `@api.onchange` raising `UserError`/`ValidationError` was found;
  period/number/etc. invariants are already enforced via `@api.constrains`.

## Items left for human review

1. **`get_views` toolbar structure** (`document.py`): the toolbar-button filtering was
   rewritten against `res["views"][view_type]["toolbar"]["action"]` (the documented
   16.0+ structure) but could not be boot-verified offline. Confirm at runtime that the
   two server-action buttons are still hidden when `disable_document_topics_wizards` is
   set. Marked with a `TODO(19.0 migration)` in the code.
2. **`tmc.category._compute_display_name` has no `@api.depends`** — intentional:
   `tmc.category` itself does not declare `parent_id` (it is declared in the subclasses
   `office`/etc.), so a base-level `@api.depends("parent_id")` is not possible. The
   stored `display_name` recomputes via the subclasses. Left as the partial migration
   had it; flag if recompute behavior looks off at runtime.
3. Re-run the security review at validation for any `res.groups`
   `category_id`→`privilege_id` and `groups_id`→`group_ids` (19.0) that may remain in
   `security/groups.xml`.

## Lint findings

pre-commit ran (ruff, ruff-format, prettier, pylint-odoo, odoo-pre-commit-hooks).
Auto-fixers (ruff-format, prettier) applied. Remaining reporter findings (non-blocking,
NOT chased this round):

- **ruff lint** in `tmc/models/document.py` (all pre-existing, unrelated to the 14→19
  migration; ruff left them because they are non-auto-fixable / unsafe):
  - `UP031` use format specifiers instead of `%` (in `_compute_name`).
  - `UP008` `super(Document, self).write(...)` → `super().write(...)`.
  - `C901` `write` is too complex (12 > 10). These are pre-existing style/complexity
    items; left untouched to keep the migration diff clean.
- **odoo-pre-commit-hooks `xml-redundant-module-name`**: several view records use
  `id="tmc.<name>"` (own module prefix). OCA style prefers dropping the prefix, but
  renaming xmlids is **intentionally deferred** — these ids are referenced cross-module
  and renaming risks dangling refs / orphaned `ir.model.data` rows (per the migration
  plan, no cosmetic xmlid renames).
- `manifest-required-author` / `missing-readme`: OCA-specific checks, N/A for a private
  module.

Note: `py_compile`/`ruff`/`xmllint` validate syntax/format only, NOT Odoo runtime API
correctness — real API validation is deferred to the boot/test stage.

## Tooling

- Added the canonical OCA 19.0 pre-commit stack (ruff + ruff-format + prettier +
  eslint + pylint-odoo + odoo-pre-commit-hooks), adapted for a non-OCA private repo
  (dropped the OCA-publishing-only hooks). Companion files: `.pylintrc`,
  `.pylintrc-mandatory`, `prettier.config.cjs`, `eslint.config.cjs`, `.editorconfig`,
  `pyproject.toml`. Existing `.gitignore` kept.

## Translations

- Translation regeneration deferred to a later stage.
