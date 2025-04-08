/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";
import { _t } from "@web/core/l10n/translation";


patch(PaymentScreen.prototype, {
    /**
     * Patched validateOrder 
     */
    setup() {
        super.setup(...arguments);
        this.to_electronic_invoice = false;
    },
    async validateOrder() {
        const MAX_VENTA=200000;
        const MAX_QTY=50;
        const to_electronic_invoice = this.currentOrder.is_to_electronic_invoice()
        const order = this.currentOrder;
        const hasSpecificQuantity = order.orderlines.some(line => {
            return line.quantity >= MAX_QTY;
        });
        if (!to_electronic_invoice) {
            this.env.services.popup.add(ErrorPopup, {
                title: _t('Debe Seleccionar Factura y Factura electrónica'),
                body: _t('Por favor seleccione en el panel derecho Factura y Factura electrónica'),                
            });
        } else if (order.get_total_with_tax() >= MAX_VENTA || hasSpecificQuantity) {
            const { confirmed } = await this.env.services.popup.add(ConfirmPopup, {
                title: _t('Valores un poco por arriba de lo normal'),
                body: _t('Quiere continuar con la venta?'),
                confirmText: _t("Yes"),
                cancelText: _t("No"),
            });
            if (confirmed) {
                return super.validateOrder(...arguments);
            } 
        } else {
            return super.validateOrder(...arguments);
        }
    },
});