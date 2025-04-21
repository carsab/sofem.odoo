/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";

patch(PosStore.prototype, {
    async printSalesReport() {
        try {
            // Aseguramos que estamos usando el ID de la sesión actualmente abierta
            if (this.posSession && this.posSession.id) {
                const params = {
                    session_ids: [this.posSession.id],
                };

                const result = await this.env.services.rpc({
                    model: 'pos.session',
                    method: 'get_closing_control_data',
                    args: [[this.posSession.id]],
                });

                return this.env.services.action.doAction('point_of_sale.action_report_pos_session_summary', {
                    additional_context: {
                        active_ids: [this.posSession.id],
                    }
                });
            }
        } catch (error) {
            console.error("Error al imprimir reporte de ventas:", error);
            this.env.services.notification.notify({
                title: this.env._t('Error'),
                message: this.env._t('No se pudo generar el reporte de ventas.'),
                type: 'danger',
            });
        }

        // Si algo falla, ejecutar el comportamiento original
        return this._super(...arguments);
    }
});