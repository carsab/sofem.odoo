/** @odoo-module */
import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";

patch(Order.prototype, {
/**
 * Patched version of the pay method for the Order class.
 * Ensures that no order line has a quantity of 0 before processing the payment.
 * If any order line has a quantity of 0, it displays an error popup.
 */
    async pay() {
        const orderLines = this.get_orderlines();
        const quantity = orderLines.map(line => line.quantity);
        if (quantity.includes(0)) {
            this.env.services.popup.add(ErrorPopup, {
                title: 'Cantidad en cero no permitida',
                body: 'Solo se permiten cantidades mayores a cero. \nRevisar cantidades por linea en la orden que esta generando.',
            });
        } else {
            return super.pay(...arguments);
        }
    },
});
