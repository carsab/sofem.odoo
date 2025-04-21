/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";

patch(PosStore.prototype, {
    async getSaleDetailsReport(options) {
        // Llamada al método original
        const original = await this._super(...arguments);

        // Verificamos si estamos en modo POS y si tenemos una sesión
        if (this.posSession && this.posSession.id) {
            try {
                // Obtener la información de resolución mediante una llamada RPC
                const resolutionInfo = await this.env.services.rpc({
                    model: 'pos.session',
                    method: 'get_resolution_data',
                    args: [[this.posSession.id]],
                });

                // Si tenemos datos de resolución, los añadimos al objeto de opciones
                if (resolutionData) {
                    options = options || {};
                    options.resolution_info = resolutionInfo;
                }
            } catch (error) {
                console.error("Error al obtener datos de resolución:", error);
            }
        }

        return original;
    },

    async _getPrintableReport(reportName, params) {
        // Si es el reporte de detalles de ventas, añadimos el ID de sesión
        if (reportName === 'point_of_sale.report_saledetails' && this.posSession) {
            params = params || {};

            // Asegurar que el ID de sesión esté incluido
            if (!params.session_ids) {
                params.session_ids = [this.posSession.id];
            }

            try {
                // Obtener datos de resolución directamente
                const resolutionInfo = await this.env.services.rpc({
                    model: 'pos.session',
                    method: 'get_resolution_data',
                    args: [[this.posSession.id]],
                });

                // Incluir datos de resolución en los parámetros
                if (resolutionData) {
                    params.resolution_info = resolutionInfo;
                }
            } catch (error) {
                console.error("Error al obtener datos de resolución:", error);
            }
        }

        return this._super(reportName, params);
    }
});