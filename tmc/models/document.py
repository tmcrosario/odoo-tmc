# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import _, api, exceptions, fields, models


class Document(models.Model):

    _name = 'tmc.document'

    name = fields.Char(
        compute='_get_name',
        store=True
    )

    dependence_id = fields.Many2one(
        comodel_name='tmc.dependence',
        domain=[('document_type_ids', '!=', False),
                ('system_ids', 'ilike', u'TMC Base')],
        string='Dependence',
        required=True
    )

    document_type_id = fields.Many2one(
        comodel_name='tmc.document_type',
        string='Document Type',
        required=True
    )

    number = fields.Integer(
        required=True
    )

    period = fields.Integer(
        required=True
    )

    date = fields.Date()

    document_object = fields.Char(
        string="Object"
    )

    document_object_copy = fields.Char(
        compute="_get_document_object_copy"
    )

    main_topic_ids = fields.Many2many(
        comodel_name='tmc.document_topic',
        relation='document_main_topic_rel',
        string='Main Topic',
        domain="[('parent_id', '=', False)]"
    )

    secondary_topic_ids = fields.Many2many(
        comodel_name='tmc.document_topic',
        relation='document_secondary_topic_rel',
        string='Secondary Topic',
        domain="[('parent_id', 'in', main_topic_ids[0][2])]"
    )

    reference_model = fields.Char(
        related='document_type_id.model'
    )

    reference_document = fields.Integer(
        compute='_get_reference_document'
    )

    highlight_ids = fields.One2many(
        comodel_name='tmc.highlight',
        inverse_name='document_id'
    )

    priority = fields.Integer(
        compute='_get_priority_and_color',
        store=True
    )

    color = fields.Char(
        compute='_get_priority_and_color',
    )

    highlights_count = fields.Integer(
        compute='_highlights_count',
        string='Highlights Count'
    )

    important = fields.Boolean(
        compute='_get_important_topic',
        store=True
    )

    _sql_constraints = [
        ('name_unique',
            'UNIQUE(name)',
            _('Document already exists'))
    ]

    @api.multi
    def show_or_add_content(self):
        reference_model = 'tmc.' + self.reference_model
        view_xmlid = 'tmc.view_' + self.reference_model + '_form'
        return {
            'type': 'ir.actions.act_window',
            'name': self.name,
            'res_model': reference_model,
            'view_type': 'form',
            'view_mode': 'form',
            'context': self._context,
            'view_id': self.env['ir.model.data'].xmlid_to_res_id(view_xmlid),
            'res_id': self.reference_document,
            'target': 'current',
            'nodestroy': True,
        }

    @api.constrains('period')
    def _check_period(self):
        period = str(self.period)
        if not len(period) == 4:
            raise Warning(_('Invalid year'))
        else:
            year = datetime.strptime(period, '%Y')
            limit = datetime.strptime('1950', '%Y')
            if year < limit or year > datetime.today():
                raise Warning(_('Invalid period'))

    @api.constrains('number')
    def _check_number(self):
        max_number = 6000
        if self.document_type_id.abbreviation == 'EXP':
            max_number = 999999
        if self.dependence_id.name in ['Concejo Municipal']:
            max_number = 999999
        if not self.number > 0 or not self.number <= max_number:
            raise Warning(_('Invalid number'))

    @api.one
    @api.depends('document_type_id.abbreviation',
                 'dependence_id.abbreviation',
                 'number',
                 'period')
    def _get_name(self):
        doc_abbr = self.document_type_id.abbreviation
        doc_number = self.number
        doc_period = self.period
        dep_abbr = self.dependence_id.abbreviation

        if (doc_abbr and doc_number and doc_period and dep_abbr):
            self.name = "%s-%s-%s/%s" % (
                doc_abbr,
                str(doc_number).zfill(6),
                dep_abbr,
                doc_period
            )
        else:
            self.name = _('Unnamed Document')

    @api.one
    @api.depends('highlight_ids')
    def _highlights_count(self):
        applicable_highlight_ids = self.highlight_ids.filtered(
            lambda record: record.applicable == True
        )
        self.highlights_count = len(applicable_highlight_ids)

    @api.multi
    @api.onchange('dependence_id')
    def _onchange_dependence(self):
        self.document_type_id = False
        document_types = self.dependence_id.document_type_ids
        if len(document_types.ids) == 1:
            self.document_type_id = document_types.ids[0]
        return {
            'domain': {
                'document_type_id': [('id', 'in', document_types.ids)]
            }
        }

    @api.multi
    @api.onchange('main_topic_ids')
    def _onchange_main_topic_ids(self):
        new_secondary_topic_ids = self.secondary_topic_ids.filtered(
            lambda record: record.parent_id in self.main_topic_ids
        )
        self.secondary_topic_ids = new_secondary_topic_ids
        return {
            'domain': {
                'secondary_topic_ids': [
                    ('first_parent_id', 'in', self.main_topic_ids.ids)
                ]
            }
        }

    @api.one
    @api.depends('document_object')
    def _get_document_object_copy(self):
        self.document_object_copy = self.document_object

    @api.one
    @api.depends('reference_model')
    def _get_reference_document(self):
        if self.reference_model:
            reference_model = 'tmc.' + self.reference_model
            reference_document = self.env[reference_model].search(
                [('document_id', '=', self.id)], limit=1)
            if reference_document:
                self.reference_document = reference_document[0]

    @api.one
    @api.depends('highlight_ids')
    def _get_priority_and_color(self):
        domain = [
            ('document_id', '=', self.id),
            ('applicable', '=', True)
        ]
        related_highlights = self.env['tmc.highlight'].search(domain)

        highest = related_highlights.sorted(
            key=lambda r: r.highlight_level_id.priority,
            reverse=True)

        if highest:
            highlight = highest[0]
            highlight_level = highlight.highlight_level_id
            self.priority = highlight_level.priority
            self.color = highlight.color

    @api.one
    @api.depends('main_topic_ids',
                 'secondary_topic_ids')
    def _get_important_topic(self):
        domain = [
            '|', ('id', 'in', self.main_topic_ids.ids),
            ('id', 'in', self.secondary_topic_ids.ids),
            ('important', '=', True)
        ]
        important_related_topics = self.env[
            'tmc.document_topic'].search(domain)

        if important_related_topics:
            self.important = True

    @api.multi
    @api.onchange('dependence_id',
                  'period',
                  'document_type_id',
                  'number')
    def _onchange_document_data(self):
        if self.dependence_id and self.document_type_id \
                and self.number and self.period:
            if self.env['tmc.document'].search([('name', '=', self.name)]):
                raise exceptions.Warning(_('Document already exists'))

