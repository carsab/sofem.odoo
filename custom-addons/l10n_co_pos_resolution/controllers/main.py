from odoo import http
from odoo.http import request
from odoo.addons.point_of_sale.controllers.main import PosController

class PosControllerExtended(PosController):
    @http.route()
    def print_sale_details(self, date_start=False, date_stop=False, session_ids=False, 
                           config_ids=False, resolution_info=None, **kwargs):
        """Sobrescribimos el método para incluir resolution_info en el contexto"""
        response = super(PosControllerExtended, self).print_sale_details(
            date_start=date_start, date_stop=date_stop, 
            session_ids=session_ids, config_ids=config_ids, **kwargs
        )
        
        # Si tenemos un ID de sesión, obtenemos los datos de resolución
        if session_ids and isinstance(session_ids, (list, tuple)) and session_ids[0]:
            session_id = session_ids[0]
            session = request.env['pos.session'].browse(int(session_id))
            
            # Obtener datos de resolución
            resolution_info = session.get_resolution_data()
            
            # Añadir al contexto si existe
            if resolution_info and isinstance(response, dict) and 'context' in response:
                response['context']['resolution_info'] = resolution_info
        
        return response