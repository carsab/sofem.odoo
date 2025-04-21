from odoo import models, fields, api
from odoo.addons.point_of_sale.models.pos_session import PosSession
import logging
_logger = logging.getLogger(__name__)

class PosSessionInherit(models.Model):
    _inherit = 'pos.session'

    def get_resolution_data(self):
        """Obtener los datos de resolución para la sesión actual"""
        self.ensure_one()
        resolution_info = {
            'has_resolution': False,
            'resolution_data': {}
        }

        _logger.info("CONSULTANDO RESOLUCION DEL POS-> %s", str(self))

        if self.config_id and self.config_id.electronic_invoice_journal_id:
            journal = self.config_id.electronic_invoice_journal_id
            _logger.info("DIARIO ASOCIADO A FE DE LA SESION POS-> %s", str(journal))

            if journal.resolution_invoice_id:
                resolution = journal.resolution_invoice_id
                _logger.info("RESOLUCION FE DE LA SESION POS-> %s", str(resolution))

                resolution_info['has_resolution'] = True
                resolution_info['resolution_data'] = {
                    'resolution_number': resolution.resolution_resolution,
                    'resolution_date':  fields.Date.to_string(resolution.resolution_resolution_date),
                    'resolution_date_from':  fields.Date.to_string(resolution.resolution_date_from),
                    'resolution_date_to': fields.Date.to_string(resolution.resolution_date_to),
                    'prefix': resolution.resolution_prefix,
                    'number_from': resolution.resolution_from,
                    'number_to': resolution.resolution_to,
                    'technical_key': resolution.resolution_technical_key,
                    'type_document_name': resolution.type_document_id.name if hasattr(resolution, 'type_document_id') else 'Factura electrónica de venta',
                }
        return resolution_info
