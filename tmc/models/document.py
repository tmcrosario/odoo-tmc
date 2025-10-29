from odoo import _, api, exceptions, fields, models
from odoo.exceptions import UserError


class Document(models.Model):
    _name = "tmc.document"
    _description = "Document"
    _order = "period desc, name desc"
    _translate = True

    # NOTE: to show specific periods in the 'searchpanel' widget
    # @api.model
    # def _get_period_selection(self):
    #     this_year = fields.Date.today().year
    #     return [(str(year), str(year)) for year in range(this_year - 6, this_year + 1)]

    name = fields.Char(compute="_compute_name", store=True, translate=True)

    dependence_id = fields.Many2one(
        comodel_name="tmc.dependence",
        domain=[
            ("document_type_ids", "!=", False),
            ("system_ids", "ilike", "TMC Base"),
        ],
        required=True,
    )

    document_type_id = fields.Many2one(comodel_name="tmc.document_type", required=True)

    document_type_abbr = fields.Char(related="document_type_id.abbreviation")

    number = fields.Integer()

    period = fields.Selection(
        selection=lambda self: [
            (str(num), str(num))
            for num in range(
                ((fields.Date.today().year) - 10),
                ((fields.Date.today().year) + 1),
            )
        ],
        required=True,
    )

    date = fields.Date()

    # NOTE: to show a mark in the name for documents related to a dictamen
    # display_name = fields.Char(compute="_compute_display_name")

    # entry_date = fields.Date(compute="_compute_entry_date", readonly=True)

    document_object = fields.Char(string="Object", size=250, index=True, translate=True)

    document_object_required = fields.Boolean()

    document_topic_ids = fields.Many2many(related="dependence_id.document_topic_ids")

    main_topic_ids = fields.Many2many(
        comodel_name="tmc.document_topic",
        relation="document_main_topic_rel",
        column1="tmc_document_id",
        column2="tmc_document_topic_id",
        domain="[('parent_id', '=', False), ('id', 'in', document_topic_ids)]",
    )

    secondary_topic_ids = fields.Many2many(
        comodel_name="tmc.document_topic",
        relation="document_secondary_topic_rel",
        domain="[('parent_id', 'in', main_topic_ids)]",
    )

    topics_display_name = fields.Char(
        compute="_compute_topics_display_name",
        string="Topics",
        readonly=True,
        translate=True,
    )

    reference_model = fields.Char(related="document_type_id.model")

    reference_document = fields.Integer(compute="_compute_reference_document")

    related_to_dictamen = fields.Boolean(
        compute="_compute_related_to_dictamen",
        store=True,
    )

    highlight_ids = fields.One2many(
        comodel_name="tmc.highlight", inverse_name="document_id"
    )

    highlights_count = fields.Integer(compute="_compute_highlights_count")

    highest_highlight = fields.Selection(
        selection=[("high", "High"), ("medium", "Medium")],
        compute="_compute_highest_highlight",
    )

    important = fields.Boolean(compute="_compute_important_topic", store=True)

    related_document_ids = fields.Many2many(
        comodel_name="tmc.document",
        relation="tmc_document_relation",
        column1="left_document_id",
        column2="right_document_id",
        domain="[('id', '!=', id)]",
    )

    # NOTE: to show specific periods in the 'searchpanel' widget
    # period_selection = fields.Selection(
    #     selection=_get_period_selection,
    #     compute="_compute_period_selection",
    #     store=True,
    # )

    _name_unique = models.Constraint("UNIQUE(name)", "Document already exists")

    @api.constrains("document_object")
    def _check_document_object_length(self):
        if len(self.document_object or "") > 125 and self.document_type_abbr != "DIC":
            raise UserError("'Object' must not exceed 125 characters.")

    @api.depends("related_document_ids")
    def _compute_related_to_dictamen(self):
        for document in self:
            has_dictamen = any(
                doc.document_type_id.abbreviation == "DIC"
                for doc in document.related_document_ids
            )
            document.update({"related_to_dictamen": has_dictamen})

    # NOTE: to show a mark in the name for documents related to a dictamen
    # def _compute_display_name(self):
    #     for document in self:
    #         if document.related_to_dictamen is True:
    #             computed_name = f"{document.name} (D)"
    #             document.display_name = computed_name
    #         else:
    #             document.display_name = document.name

    # NOTE: to show specific periods in the 'searchpanel' widget
    # @api.onchange("period")
    # def _onchange_period(self):
    #     self._compute_period_selection()

    def show_or_add_content(self):
        reference_model = "tmc." + self.reference_model
        view_xmlid = "tmc.view_" + self.reference_model + "_form"
        return {
            "type": "ir.actions.act_window",
            "name": self.name,
            "res_model": reference_model,
            "view_type": "form",
            "view_mode": "form",
            "context": self.env.context,
            "view_id": self.env["ir.model.data"].xmlid_to_res_id(view_xmlid),
            "res_id": self.reference_document,
            "target": "current",
            "nodestroy": True,
        }

    @api.constrains("period")
    def _check_period(self):
        period = int(self.period)
        if not (1000 <= period <= fields.Date.today().year):
            raise exceptions.ValidationError(_("Invalid period"))
        if period < 1948:
            raise exceptions.ValidationError(_("Periods before 1948 are not allowed."))

    @api.constrains("number")
    def _check_number(self):
        max_number = 6000
        if self.document_type_id.abbreviation in ["EXP", "ACT", "CONV"]:
            max_number = 999999
        if self.dependence_id.abbreviation in ["CM", "HCM", "CONC"]:
            max_number = 999999
        if self.dependence_id.abbreviation in ["DHH"]:
            max_number = 9999
        if self.number == 0 and self.document_type_id.abbreviation != "ACT":
            raise UserError(_("Invalid number"))
        if self.number > max_number:
            raise UserError(_("Invalid number"))

    @api.depends("document_type_id", "dependence_id", "number", "period")
    def _compute_name(self):
        for document in self:
            doc_abbr = document.document_type_id.abbreviation
            doc_number = document.number
            doc_period = document.period
            dep_abbr = document.dependence_id.abbreviation

            if doc_abbr == "ACT":
                doc_number = self.env.ref("tmc_data.seq_tmc_act").number_next_actual

            if doc_abbr and doc_number and doc_period and dep_abbr:
                document.name = "%s-%s-%s/%s" % (
                    doc_abbr,
                    str(doc_number).zfill(6),
                    dep_abbr,
                    doc_period,
                )
            else:
                document.name = _("Unnamed Document")

    @api.depends("highlight_ids")
    def _compute_highlights_count(self):
        for document in self:
            applicable_highlight_ids = document.highlight_ids.filtered(
                lambda record: record.applicable is True
            )
            document.highlights_count = len(applicable_highlight_ids)

    @api.onchange("main_topic_ids")
    def _onchange_main_topic_ids(self):
        if "Varios" in self.main_topic_ids.mapped("name"):
            self.document_object_required = True
        else:
            self.document_object_required = False

        new_secondary_topic_ids = self.secondary_topic_ids.filtered(
            lambda r: r.parent_id.id in self.main_topic_ids._origin.mapped("id")
        )
        self.secondary_topic_ids = new_secondary_topic_ids

        return {
            "domain": {
                "secondary_topic_ids": [
                    (
                        "first_parent_id",
                        "in",
                        self.main_topic_ids._origin.mapped("id"),
                    )
                ]
            }
        }

    @api.depends("reference_model")
    def _compute_reference_document(self):
        for document in self:
            document.reference_document = None
            if document.reference_model:
                reference_model = "tmc." + document.reference_model
                reference_document = document.env[reference_model].search(
                    [("document_id", "=", document.id)], limit=1
                )
                if reference_document:
                    document.reference_document = reference_document[0]

    @api.depends("highlight_ids")
    def _compute_highest_highlight(self):
        for document in self:
            document.highest_highlight = None
            high_highlights = self.env["tmc.highlight"].search(
                [
                    ("document_id", "=", document.id),
                    ("applicable", "=", True),
                    ("level", "=", "high"),
                ]
            )
            medium_highlights = self.env["tmc.highlight"].search(
                [
                    ("document_id", "=", document.id),
                    ("applicable", "=", True),
                    ("level", "=", "medium"),
                ]
            )
            if high_highlights:
                document.highest_highlight = "high"
            elif medium_highlights:
                document.highest_highlight = "medium"

    @api.depends("main_topic_ids", "secondary_topic_ids")
    def _compute_important_topic(self):
        for document in self:
            domain = [
                "|",
                ("id", "in", document.main_topic_ids.ids),
                ("id", "in", document.secondary_topic_ids.ids),
                ("important", "=", True),
            ]
            important_related_topics = self.env["tmc.document_topic"].search(domain)

            if important_related_topics:
                document.important = True
            else:
                document.important = False

    @api.onchange("dependence_id", "document_type_id", "period", "number")
    def _onchange_document_data(self):
        if self.dependence_id and self.document_type_id and self.number and self.period:
            if self.env["tmc.document"].search([("name", "=", self.name)]):
                raise UserError(_("Document already exists"))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            doc_type = vals.get("document_type_id")
            doc_type_abbr = self.env["tmc.document_type"].browse(doc_type).abbreviation

            if vals.get("date"):
                if (
                    str(int(vals.get("date")[:4])) != str(vals.get("period"))
                    and doc_type_abbr != "CONV"
                ):
                    message = _("Date does not match with period")
                    raise exceptions.UserError(message)

            if doc_type_abbr == "ACT":
                vals["number"] = self.env.ref("tmc_data.seq_tmc_act").number_next_actual
                seq = self.env["ir.sequence"]
                seq.next_by_code("tmc.document")

        return super().create(vals_list)

    def write(self, vals, write_inverse=True):
        if vals.get("main_topic_ids"):
            message = _("You must specify a period.")
            # Handle different possible formats of main_topic_ids
            main_topics = vals["main_topic_ids"]
            if main_topics and isinstance(main_topics, list) and len(main_topics) > 0:
                if (
                    isinstance(main_topics[0], (list, tuple))
                    and len(main_topics[0]) > 2
                ):
                    main_topics_set = set(main_topics[0][2])
                else:
                    main_topics_set = set()
            else:
                main_topics_set = set()

            mp_topic = self.env.ref("tmc_data.tmc_document_topic_modifica_presupuesto")
            p_topic = self.env.ref("tmc_data.tmc_document_topic_periodo")

            p_topic_map = p_topic.mapped("id")
            if main_topics_set.intersection(p_topic_map):
                if vals.get("secondary_topic_ids"):
                    domain = [
                        ("id", "in", vals["secondary_topic_ids"][0][2]),
                        ("parent_id", "=", p_topic.id),
                    ]
                    if not self.env["tmc.document_topic"].search(domain):
                        raise exceptions.UserError(message)
                else:
                    raise exceptions.UserError(message)
            else:
                mp_topic_map = mp_topic.mapped("id")
                if main_topics_set.intersection(mp_topic_map):
                    raise exceptions.UserError(message)

        if vals.get("date"):
            if (
                int(vals.get("date")[:4]) != self.period
                and self.document_type_id.abbreviation != "CONV"
            ):
                message = _("Date does not match with period")
                raise exceptions.UserError(message)

        if write_inverse and vals.get("related_document_ids"):
            new_related_documents = self.browse(vals["related_document_ids"][0][2])
            new_related_documents.write(
                {"related_document_ids": [(4, self.id)]}, write_inverse=False
            )
            current_rd_map = self.related_document_ids.mapped("id")
            new_rd_map = new_related_documents.mapped("id")
            new_rd_set = set(new_rd_map)
            rd_diff = [x for x in current_rd_map if x not in new_rd_set]
            if rd_diff:
                self.browse(rd_diff).write(
                    {"related_document_ids": [(3, self.id)]},
                    write_inverse=False,
                )

        return super(Document, self).write(vals)

    def lookahead(self, iterable):
        """Pass through all values from the given iterable, augmented by the
        information if there are more values to come after the current one
        (True), or if it is the last value (False).
        """
        # Get an iterator from the iterable
        iterator = iter(iterable)

        # Get the first item from the iterator, or None if the iterator is empty
        prev = next(iterator, None)

        # Iterate through the remaining items in the iterator
        for item in iterator:
            # Yield the previous item and the "more to come" flag
            yield prev, True
            # Set the previous item to the current item
            prev = item

        # If the iterator was not empty, yield the last item and the "last item" flag
        if prev:
            yield prev, False

    @api.depends("main_topic_ids", "secondary_topic_ids")
    def _compute_topics_display_name(self):
        for document in self:
            document.topics_display_name = ""
            if document.main_topic_ids:
                for main_topic, has_more_main_topic in self.lookahead(
                    document.main_topic_ids
                ):
                    aux = ""
                    aux += main_topic.name
                    sec_topic_filtered = document.secondary_topic_ids.filtered(
                        lambda record: record.parent_id.id == main_topic.id
                    )
                    is_first = True
                    for sec_topic, has_more_sec_topic in self.lookahead(
                        sec_topic_filtered
                    ):
                        if sec_topic.parent_id == main_topic:
                            if is_first:
                                is_first = False
                                aux += " ("
                            aux += sec_topic.name
                            if has_more_sec_topic:
                                aux += ", "
                            else:
                                aux += ")"
                    if has_more_main_topic:
                        aux += ", "
                    document.topics_display_name += aux

    @api.onchange("document_object")
    def _onchange_document_object(self):
        if self.document_object:
            self.document_object = self.document_object.title()

    def _compute_entry_date(self):
        for document in self:
            raa_object = self.env["raa.registry_aa"].search(
                [("document_id", "=", document.id)]
            )
            if raa_object:
                document.entry_date = raa_object.entry_date
            else:
                document.entry_date = fields.Date.from_string(
                    document.create_date
                ).strftime("%Y-%m-%d")

    def action_mass_edit_document_topics_show_wizard(self, remove=False):
        active_model = self.env.context.get("active_model")
        active_id = self.env.context.get("active_id")

        dependence_id = self.env[active_model].browse(active_id).dependence_id.id

        new_context = dict(
            self.env.context,
            default_dependence_id=dependence_id,
            remove_document_topics=remove,
        )

        return {
            "type": "ir.actions.act_window",
            "name": _("Remove Document Topics") if remove else _("Add Document Topics"),
            "res_model": "tmc.mass_edit_document_topics_wizard",
            "target": "new",
            "view_id": self.env.ref("tmc.view_mass_edit_document_topics_form").id,
            "view_mode": "form",
            "context": new_context,
        }

    def fields_view_get(
        self, view_id=None, view_type="list", toolbar=False, submenu=False
    ):
        res = super(Document, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )

        if "disable_document_topics_wizards" in self.env.context:
            add_document_topics_button_id = (
                self.env.ref("tmc.add_document_topics_action_server").id or False
            )
            remove_document_topics_button_id = (
                self.env.ref("tmc.remove_document_topics_action_server").id or False
            )
            for button in res.get("toolbar", {}).get("action", []):
                if (
                    add_document_topics_button_id
                    and button["id"] == add_document_topics_button_id
                ):
                    res["toolbar"]["action"].remove(button)
            for button in res.get("toolbar", {}).get("action", []):
                if (
                    remove_document_topics_button_id
                    and button["id"] == remove_document_topics_button_id
                ):
                    res["toolbar"]["action"].remove(button)

        return res


class DocumentDec(models.Model):
    _name = "tmc.document_dec"
    _description = "Decreto"
    _inherits = {'tmc.document': 'document_id'}

    document_id = fields.Many2one(
        comodel_name="tmc.document",
        domain=[("document_type_id.abbreviation", "=", "DEC")],
        string="Document Name",
        required=True,
        ondelete="cascade",
    )


class DocumentDic(models.Model):
    _name = "tmc.document_dic"
    _description = "Dictamen"
    _inherits = {'tmc.document': 'document_id'}

    document_id = fields.Many2one(
        comodel_name="tmc.document",
        domain=[("document_type_id.abbreviation", "=", "DIC")],
        string="Document Name",
        required=True,
        ondelete="cascade",
    )


class DocumentExp(models.Model):
    _name = "tmc.document_exp"
    _description = "Expediente"
    _inherits = {'tmc.document': 'document_id'}

    document_id = fields.Many2one(
        comodel_name="tmc.document",
        domain=[("document_type_id.abbreviation", "=", "EXP")],
        string="Document Name",
        required=True,
        ondelete="cascade",
    )


class DocumentExt(models.Model):
    _name = "tmc.document_ext"
    _description = "Resolucion Extraordinaria"
    _inherits = {'tmc.document': 'document_id'}

    document_id = fields.Many2one(
        comodel_name="tmc.document",
        domain=[("document_type_id.abbreviation", "=", "EXT")],
        string="Document Name",
        required=True,
        ondelete="cascade",
    )


class DocumentLeg(models.Model):
    _name = "tmc.document_leg"
    _description = "Legajo"
    _inherits = {'tmc.document': 'document_id'}

    document_id = fields.Many2one(
        comodel_name="tmc.document",
        domain=[("document_type_id.abbreviation", "=", "LEG")],
        string="Document Name",
        required=True,
        ondelete="cascade",
    )


class DocumentOrd(models.Model):
    _name = "tmc.document_ord"
    _description = "Ordenanza"
    _inherits = {'tmc.document': 'document_id'}

    document_id = fields.Many2one(
        comodel_name="tmc.document",
        domain=[("document_type_id.abbreviation", "=", "ORD")],
        string="Document Name",
        required=True,
        ondelete="cascade",
    )


class DocumentRes(models.Model):
    _name = "tmc.document_res"
    _description = "Resolucion"
    _inherits = {'tmc.document': 'document_id'}

    document_id = fields.Many2one(
        comodel_name="tmc.document",
        domain=[("document_type_id.abbreviation", "=", "RES")],
        string="Document Name",
        required=True,
        ondelete="cascade",
    )


class DocumentConv(models.Model):
    _name = "tmc.document_conv"
    _description = "Convenio"
    _inherits = {'tmc.document': 'document_id'}

    document_id = fields.Many2one(
        comodel_name="tmc.document",
        domain=[("document_type_id.abbreviation", "=", "CONV")],
        string="Document Name",
        required=True,
        ondelete="cascade",
    )


class DocumentAct(models.Model):
    _name = "tmc.document_act"
    _description = "Acta"
    _inherits = {'tmc.document': 'document_id'}

    document_id = fields.Many2one(
        comodel_name="tmc.document",
        domain=[("document_type_id.abbreviation", "=", "ACT")],
        string="Document Name",
        required=True,
        ondelete="cascade",
    )
