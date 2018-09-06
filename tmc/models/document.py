# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import _, api, exceptions, fields, models


class Document(models.Model):

    _name = 'tmc.document'
    _order = 'period desc, name desc'

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

    document_type_abbr = fields.Char(
        related='document_type_id.abbreviation',
    )

    number = fields.Integer()

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

    topics_display_name = fields.Char(
        compute='_compute_topics_display_name',
        string='Topics',
        readonly=True,
        store=True
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

    related_document_ids = fields.Many2many(
        comodel_name='tmc.document',
        relation='tmc_document_relation',
        column1='left_document_id',
        column2='right_document_id',
        domain="[('id', '!=', id)]"
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
        if self.document_type_id.abbreviation in ['EXP', 'ACT', 'CONV']:
            max_number = 999999
        if self.dependence_id.abbreviation in ['CM', 'HCM', 'CONC']:
            max_number = 999999
        if self.number == 0 and self.document_type_id.abbreviation != 'ACT':
            raise Warning(_('Invalid number'))
        if self.number > max_number:
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

            if doc_abbr == 'ACT':
                doc_number = self.env.ref(
                    'tmc_data.seq_tmc_act').number_next_actual

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
            if document.document_object:
                if len(document.document_object) > 45:
                    string = document.document_object[:45] + '...'
                else:
                    string = document.document_object
                document.document_object_copy = string.title()

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

    @api.model
    def create(self, vals):
        if vals.get('document_type_abbr') == 'ACT':
            vals['number'] = self.env.ref(
                'tmc_data.seq_tmc_act').number_next_actual
            seq = self.env['ir.sequence']
            seq.next_by_code('tmc.document')
        return super(Document, self).create(vals)

    @api.multi
    def write(self, vals, write_inverse=True):
        if vals.get('main_topic_ids'):
            message = _('You must specify a period.')
            main_topics_set = set(vals['main_topic_ids'][0][2])

            mp_topic = self.env.ref(
                'tmc_data.tmc_document_topic_modifica_presupuesto')
            p_topic = self.env.ref(
                'tmc_data.tmc_document_topic_periodo')

            p_topic_map = p_topic.mapped('id')
            if main_topics_set.intersection(p_topic_map):
                if vals.get('secondary_topic_ids'):
                    domain = [
                        ('id', 'in', vals['secondary_topic_ids'][0][2]),
                        ('parent_id', '=', p_topic.id)
                    ]
                    if not self.env['tmc.document_topic'].search(domain):
                        raise exceptions.UserError(message)
                else:
                    raise exceptions.UserError(message)
            else:
                mp_topic_map = mp_topic.mapped('id')
                if main_topics_set.intersection(mp_topic_map):
                    raise exceptions.UserError(message)

        if write_inverse and vals.get('related_document_ids'):
            new_related_documents = self.browse(
                vals['related_document_ids'][0][2])
            new_related_documents.write(
                {'related_document_ids': [(4, self.id)]},
                write_inverse=False
            )
            current_rd_map = self.related_document_ids.mapped('id')
            new_rd_map = new_related_documents.mapped('id')
            new_rd_set = set(new_rd_map)
            rd_diff = [x for x in current_rd_map if x not in new_rd_set]
            if rd_diff:
                self.browse(rd_diff).write(
                    {'related_document_ids': [(3, self.id)]},
                    write_inverse=False
                )

        return super(Document, self).write(vals)

    def lookahead(self, iterable):
        """Pass through all values from the given iterable, augmented by the
        information if there are more values to come after the current one
        (True), or if it is the last value (False).
        """
        # Get an iterator and pull the first value
        it = iter(iterable)
        last = next(it)
        # Run the iterator to exhaustion (starting from the second value)
        for val in it:
            # Report the *previous* value (more to come)
            yield last, True
            last = val
        # Report the last value
        yield last, False

    @api.multi
    @api.depends('main_topic_ids',
                 'secondary_topic_ids')
    def _compute_topics_display_name(self):
        for document in self:
            document.topics_display_name = ''
            if document.main_topic_ids:
                for mt, has_more_mt in self.lookahead(document.main_topic_ids):
                    aux = ''
                    aux += mt.name
                    st_filtered = document.secondary_topic_ids.filtered(
                        lambda record: record.parent_id.id == mt.id
                    )
                    is_first = True
                    for st, has_more_st in self.lookahead(st_filtered):
                        if st.parent_id == mt:
                            if is_first:
                                is_first = False
                                aux += ' ('
                            aux += st.name
                            if has_more_st:
                                aux += ', '
                            else:
                                aux += ')'
                    if has_more_mt:
                        aux += ', '
                    document.topics_display_name += aux

    @api.multi
    @api.onchange('document_object')
    def _onchange_document_object(self):
        if self.document_object:
            self.document_object = self.document_object.title()


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


class DocumentConv(models.Model):
    _name = 'tmc.document_conv'

    document_id = fields.Many2one(
        comodel_name='tmc.document',
        domain=[('document_type_id.abbreviation', '=', 'CONV')],
        string='Document Name',
        required=True,
        ondelete='cascade',
        delegate=True
    )


class DocumentAct(models.Model):
    _name = 'tmc.document_act'

    document_id = fields.Many2one(
        comodel_name='tmc.document',
        domain=[('document_type_id.abbreviation', '=', 'ACT')],
        string='Document Name',
        required=True,
        ondelete='cascade',
        delegate=True
    )
