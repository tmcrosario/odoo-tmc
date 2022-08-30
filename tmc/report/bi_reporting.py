from datetime import date, datetime

from odoo import models


class Report(models.Model):

    _name = "tmc.report"
    _description = "Report Template"

    def format_date(self, date_string):
        if date_string:
            try:
                formatted_date = date.strftime(date_string, "%d/%m/%Y")
            except ValueError:
                formatted_date = datetime.strptime(
                    date_string, "%d/%m/%Y %H:%M:%S"
                ).date()
            return formatted_date

    def _prepare_report(self):
        context = self._context.copy()
        return self.with_context(context)

    def generate_report(self):
        self.ensure_one()
        report_name = self.env.context.get("report_name")
        if report_name:
            self = self._prepare_report()
            report = self.env.ref(report_name)
            return report.report_action(self)
        return None
