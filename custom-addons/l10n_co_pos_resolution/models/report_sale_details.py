from odoo import models, api
from odoo.addons.point_of_sale.models.report_sale_details import ReportSaleDetails

import logging
_logger = logging.getLogger(__name__)

class ReportSaleDetailsInherit(models.AbstractModel):
    _inherit = 'report.point_of_sale.report_saledetails'
    
    @api.model
    def get_sale_details(self, date_start=False, date_stop=False, config_ids=False, session_ids=False):
        # Primero llamamos al método original
        _logger.debug("Llamando a get_sale_details con config_ids: %s, session_ids: %s", config_ids, session_ids)
        # Llamamos al método original para obtener los detalles de la venta
        result = super(ReportSaleDetailsInherit, self).get_sale_details(
            date_start=date_start, date_stop=date_stop, 
            config_ids=config_ids, session_ids=session_ids
        )
        _logger.debug("RESULTADO DEL LLAMADO AL SUPER %s", result)
        
        # Inicializamos resolution_data como False para evitar errores en la plantilla        
        result['resolution_info'] = {
            'has_resolution': False,
            'resolution_data': {}
        }
        
        # Verificar si tenemos session_ids
        if session_ids and isinstance(session_ids, list) and session_ids:
            try:
                # Obtener la sesión
                session = self.env['pos.session'].browse(session_ids[0])
                # Verificar si existe el método get_resolution_data
                if hasattr(session, 'get_resolution_data') and callable(session.get_resolution_data):
                    resolution_info = session.get_resolution_data()
                    if resolution_info:
                        result['resolution_info'] = resolution_info
                    _logger.info("INFORMACION DE REPORTE CON RESOLUCION DEL POS ::> %s", str(result))   
                    _logger.info("CONTEXTO ::> %s", str(self.env.context))    
                    _logger.info("COMPANY_NAME::> %s", str(self.env.company_name))   

            except Exception as e:
                # Registrar el error pero continuar
                _logger.error("Error al obtener datos de resolución: %s", str(e))
        
        # Verificar si los datos de resolución están en el contexto
        if not result.get('resolution_info') and self.env.context.get('resolution_info'):
            result['resolution_info'] = self.env.context.get('resolution_info')
        
        return result