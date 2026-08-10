import base64

from odoo import api, models
from odoo.tools import file_open
from odoo.tools.image import image_data_uri

LOGO_PATH = "tmc/static/src/img/report_logo.png"


class ReportLogo(models.AbstractModel):
    _name = "tmc.report_logo"
    _description = "Institutional Logo for Printed Reports"

    @api.model
    def data_uri(self):
        # Inlined so wkhtmltopdf never fetches it over the network
        with file_open(LOGO_PATH, "rb") as logo:
            return image_data_uri(base64.b64encode(logo.read()))
