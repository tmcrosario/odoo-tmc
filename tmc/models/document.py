# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import _, api, exceptions, fields, models


class Document(models.Model):

    _name = 'tmc.document'

    name = fields.Char(
        compute='_compute_name',
        store=True
    )

    dependence_id = fields.Many2one(
        comodel_name='tmc.dependence',
        domain=[('document_type_ids', '!=', False),
                ('system_ids', 'ilike', u'TMC Base')],
        required=True
    )

    document_type_id = fields.Many2one(
        comodel_name='tmc.document_type',
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
        string='Object',
        index=True
    )

    document_object_required = fields.Boolean()

    document_object_copy = fields.Char(
        compute='_compute_document_object_copy'
    )

    document_topic_ids = fields.Many2many(
        related='dependence_id.document_topic_ids'
    )

    main_topic_ids = fields.Many2many(
        comodel_name='tmc.document_topic',
        relation='document_main_topic_rel',
        domain="[('parent_id', '=', False), ('id', 'in', document_topic_ids[0][2])]"
    )

    secondary_topic_ids = fields.Many2many(
        comodel_name='tmc.document_topic',
        relation='document_secondary_topic_rel',
        domain="[('parent_id', 'in', main_topic_ids[0][2])]"
    )

    reference_model = fields.Char(
        related='document_type_id.model'
    )

    reference_document = fields.Integer(
        compute='_compute_reference_document'
    )

    highlight_ids = fields.One2many(
        comodel_name='tmc.highlight',
        inverse_name='document_id'
    )

    highlights_count = fields.Integer(
        compute='_compute_highlights_count'
    )

    highest_highlight = fields.Selection(
        selection=[('high', 'High'),
                   ('medium', 'Medium')],
        compute='_compute_highest_highlight'

    )

    important = fields.Boolean(
        compute='_compute_important_topic',
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
        if self.dependence_id.abbreviation in ['CM', 'HCM']:
            max_number = 999999
        if not self.number > 0 or not self.number <= max_number:
            raise Warning(_('Invalid number'))

    @api.multi
    @api.depends('document_type_id',
                 'dependence_id',
                 'number',
                 'period')
    def _compute_name(self):
        for document in self:
            doc_abbr = document.document_type_id.abbreviation
            doc_number = document.number
            doc_period = document.period
            dep_abbr = document.dependence_id.abbreviation

            if (doc_abbr and doc_number and doc_period and dep_abbr):
                document.name = "%s-%s-%s/%s" % (
                    doc_abbr,
                    str(doc_number).zfill(6),
                    dep_abbr,
                    doc_period
                )
            else:
                document.name = _('Unnamed Document')

    @api.multi
    @api.depends('highlight_ids')
    def _compute_highlights_count(self):
        for document in self:
            applicable_highlight_ids = document.highlight_ids.filtered(
                lambda record: record.applicable == True
            )
            document.highlights_count = len(applicable_highlight_ids)

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
        if u'Varios' in self.main_topic_ids.mapped('name'):
            self.document_object_required = True
        else:
            self.document_object_required = False
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

    @api.multi
    @api.depends('document_object')
    def _compute_document_object_copy(self):
        for document in self:
            document.document_object_copy = document.document_object

    @api.multi
    @api.depends('reference_model')
    def _compute_reference_document(self):
        for document in self:
            if document.reference_model:
                reference_model = 'tmc.' + document.reference_model
                reference_document = document.env[reference_model].search(
                    [('document_id', '=', document.id)], limit=1)
                if reference_document:
                    document.reference_document = reference_document[0]

    @api.multi
    @api.depends('highlight_ids')
    def _compute_highest_highlight(self):
        for document in self:
            high_highlights = self.env['tmc.highlight'].search([
                ('document_id', '=', document.id),
                ('applicable', '=', True),
                ('level', '=', 'high')]
            )
            medium_highlights = self.env['tmc.highlight'].search([
                ('document_id', '=', document.id),
                ('applicable', '=', True),
                ('level', '=', 'medium')]
            )
            if high_highlights:
                document.highest_highlight = 'high'
            elif medium_highlights:
                document.highest_highlight = 'medium'

    @api.multi
    @api.depends('main_topic_ids',
                 'secondary_topic_ids')
    def _compute_important_topic(self):
        for document in self:
            domain = [
                '|', ('id', 'in', document.main_topic_ids.ids),
                ('id', 'in', document.secondary_topic_ids.ids),
                ('important', '=', True)
            ]
            important_related_topics = self.env[
                'tmc.document_topic'].search(domain)

            if important_related_topics:
                document.important = True

    @api.multi
    @api.onchange('dependence_id',
                  'document_type_id',
                  'period',
                  'number')
    def _onchange_document_data(self):
        if self.dependence_id and self.document_type_id \
                and self.number and self.period:
            if self.env['tmc.document'].search([('name', '=', self.name)]):
                raise exceptions.Warning(_('Document already exists'))


class DocumentDec(models.Model):
    _name = 'tmc.document_dec'

    document_id = fields.Many2one(
        comodel_name='tmc.document',
        domain=[('document_type_id.abbreviation', '=', 'DEC')],
        string='Document Name',
        required=True,
        ondelete='cascade',
        delegate=True
    )


class DocumentDic(models.Model):
    _name = 'tmc.document_dic'

    document_id = fields.Many2one(
        comodel_name='tmc.document',
        domain=[('document_type_id.abbreviation', '=', 'DIC')],
        string='Document Name',
        required=True,
        ondelete='cascade',
        delegate=True
    )


class DocumentExp(models.Model):
    _name = 'tmc.document_exp'

    document_id = fields.Many2one(
        comodel_name='tmc.document',
        domain=[('document_type_id.abbreviation', '=', 'EXP')],
        string='Document Name',
        required=True,
        ondelete='cascade',
        delegate=True
    )


class DocumentExt(models.Model):
    _name = 'tmc.document_ext'

    document_id = fields.Many2one(
        comodel_name='tmc.document',
        domain=[('document_type_id.abbreviation', '=', 'EXT')],
        string='Document Name',
        required=True,
        ondelete='cascade',
        delegate=True
    )


class DocumentLeg(models.Model):
    _name = 'tmc.document_leg'

    document_id = fields.Many2one(
        comodel_name='tmc.document',
        domain=[('document_type_id.abbreviation', '=', 'LEG')],
        string='Document Name',
        required=True,
        ondelete='cascade',
        delegate=True
    )


class DocumentOrd(models.Model):
    _name = 'tmc.document_ord'

    document_id = fields.Many2one(
        comodel_name='tmc.document',
        domain=[('document_type_id.abbreviation', '=', 'ORD')],
        string='Document Name',
        required=True,
        ondelete='cascade',
        delegate=True
    )


class DocumentRes(models.Model):
    _name = 'tmc.document_res'

    document_id = fields.Many2one(
        comodel_name='tmc.document',
        domain=[('document_type_id.abbreviation', '=', 'RES')],
        string='Document Name',
        required=True,
        ondelete='cascade',
        delegate=True
    )
