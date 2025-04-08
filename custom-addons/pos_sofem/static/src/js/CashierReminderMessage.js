/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";

/**
 * Componente independiente para mostrar recordatorios a los cajeros
 */
export class CashierReminderMessage extends Component {
    static template = 'pos_cashier_reminder.ReminderMessageTemplate';

    setup() {
        this.pos = usePos();
        this.state = useState({
            message: "RECORDATORIO: No olvides preguntar al cliente si requiere factura a nombre propio",
            isVisible: true
        });
    }

    hideMessage() {
        this.state.isVisible = false;
    }
}

patch(ProductScreen.prototype, {
    setup() {
        super.setup();
        this.reminderState = useState({
            message: "RECORDATORIO: No olvides preguntar al cliente si requiere factura a nombre propio",
            isVisible: true
        });
    },

    hideReminder() {
        this.reminderState.isVisible = false;
    }
});