/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { SaleDetailsButton } from "@point_of_sale/app/navbar/sale_details_button/sale_details_button";

patch(SaleDetailsButton.prototype, {
    /**
     * Sobrescribe el método onClick para incluir la información de resolución
     * al generar el reporte de ventas del POS
     */
    async onClick() {
        const currentSession = this.pos.posSession;

        try {
            // Verificar si estamos en una sesión activa
            if (currentSession && currentSession.id) {
                // Obtener datos de resolución mediante llamada RPC
                const resolutionInfo = await this.env.services.rpc({
                    model: 'pos.session',
                    method: 'get_resolution_data',
                    args: [[currentSession.id]],
                });

                // Verificar lógica de flujo basada en la configuración
                if (this.pos.config.cash_control && this.pos.config.session_log_with_session_state && this.pos.posSession.state !== 'closed') {
                    this.openSessionDetailsPopup();
                    return;
                }

                // Mostrar diálogo de confirmación
                const { confirmed } = await this.showPopup('ConfirmPopup', {
                    title: this.env._t('Print Sales Details'),
                    body: this.env._t('Would you like to print the sales details?'),
                });

                if (confirmed) {
                    // Definimos los parámetros del reporte
                    let params = {
                        session_ids: [currentSession.id],
                    };

                    // Solo añadimos resolution_info si existe
                    if (resolutionInfo) {
                        // Preparar el contexto para el reporte
                        const reportContext = {
                            resolution_info: resolutionInfo
                        };

                        // Pre-procesar los datos para asegurar que el reporte tenga la información
                        await this.env.services.rpc({
                            model: 'report.point_of_sale.report_saledetails',
                            method: 'get_sale_details',
                            args: [false, false, false, [currentSession.id]],
                            kwargs: {
                                context: reportContext
                            }
                        });
                    }

                    // Imprimir el reporte con los parámetros
                    await this.env.proxy.printer.printXmlReceipt({
                        title: this.env._t('Sales Details'),
                        url: '/report/pdf/point_of_sale.report_saledetails',
                        params: params,
                    });
                }
                return;
            }
        } catch (error) {
            console.error("Error al procesar detalles de venta:", error);
        }

        // Comportamiento predeterminado si algo falla
        await this._super(...arguments);
    }
});