from datetime import datetime
from odoo import models


class Report(models.Model):

    _name = 'tmc.report'
    _description = 'Report Template'

    def format_date(self, date_string):
        formatted_date = None
        if date_string:
            try:
                tmp = datetime.strptime(date_string, '%Y-%m-%d')
            except ValueError:
                tmp = datetime.strptime(date_string,
                                        '%Y-%m-%d %H:%M:%S').date()
            finally:
                formatted_date = tmp.strftime('%d/%m/%Y')
        return formatted_date

    def _prepare_report(self):
        context = self._context.copy()
        return self.with_context(context)

    def generate_report(self):
        res = {}
        self.ensure_one()
        report_name = self.env.context.get('report_name')
        if report_name:
            self = self._prepare_report()
            res = {
                'type': 'ir.actions.report',
                'report_name': report_name,
                'report_type': 'py3o'
            }
        return res
