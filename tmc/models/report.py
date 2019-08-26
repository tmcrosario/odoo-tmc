
from datetime import datetime

from odoo import api, models


class Report(models.Model):

    _name = 'tmc.report'

    @api.multi
    def format_date(self, date_string):
        formatted_date = None
        if date_string:
            try:
                tmp = datetime.strptime(
                    date_string, '%Y-%m-%d')
            except Exception:
                tmp = datetime.strptime(
                    date_string, '%Y-%m-%d %H:%M:%S').date()
            finally:
                formatted_date = tmp.strftime('%d/%m/%Y')
        return formatted_date

    @api.multi
    def _prepare_report(self):
        context = self._context.copy()
        return self.with_context(context)

    @api.multi
    def generate_report(self):
        self.ensure_one()
        report_name = self.env.context.get('report_name')
        if report_name:
            self = self._prepare_report()
            return self.env['report'].get_action(
                self, report_name)
