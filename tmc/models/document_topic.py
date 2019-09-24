from odoo import api, fields, models


class DocumentTopic(models.Model):

    _name = 'tmc.document_topic'
    _description = 'document_topic'
    _inherit = 'tmc.category'
    _order = 'name'

    first_parent_id = fields.Many2one(
        comodel_name='tmc.document_topic',
        compute='_compute_first_parent',
        store=True
    )

    document_ids = fields.Many2many(
        comodel_name='tmc.document',
        relation='document_main_topic_rel',
        column1='main_topic_ids'
    )

    parent_id = fields.Many2one(
        comodel_name='tmc.document_topic',
        string='Main Topic'
    )

    child_ids = fields.One2many(
        comodel_name='tmc.document_topic',
        inverse_name='parent_id'
    )

    dependence_ids = fields.Many2many(
        comodel_name='tmc.dependence',
        domain="[('abbreviation', '!=', False)]"
    )

    dependences_display_name = fields.Char(
        compute='_compute_dependences_display_name',
        string='Dependences'
    )

    secondary_topics_display_name = fields.Char(
        compute='_compute_secondary_topics_display_name',
        string='Secondary Topics'
    )

    important = fields.Boolean()

    color = fields.Integer()

    @api.multi
    @api.depends('parent_id',
                 'parent_id.parent_id')
    def _compute_first_parent(self):
        for document_topic in self:
            first_parent_id = False
            parent = document_topic.parent_id
            while parent:
                first_parent_id = parent.id
                parent = parent.parent_id
            document_topic.first_parent_id = first_parent_id

    @api.multi
    def _compute_display_name(self):
        for topic in self:
            topic.display_name = topic.name

    @api.multi
    @api.depends('dependence_ids')
    def _compute_dependences_display_name(self):
        for document_topic in self:
            if document_topic.dependence_ids:
                document_topic.dependences_display_name = ', '.join(
                    document_topic.dependence_ids.mapped('abbreviation'))

    @api.multi
    @api.depends('child_ids')
    def _compute_secondary_topics_display_name(self):
        for document_topic in self:
            if document_topic.child_ids:
                document_topic.secondary_topics_display_name = ', '.join(
                    document_topic.child_ids.mapped('name'))
