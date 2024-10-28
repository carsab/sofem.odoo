/** @odoo-module */
import {patch} from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { useService } from "@web/core/utils/hooks";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";

patch(PaymentScreen.prototype, {
  /**
   * Patched validateOrder 
   */
    setup() {
        super.setup(...arguments);
        this.to_electronic_invoice = false;
    },
      async validateOrder() {
          const to_electronic_invoice = this.currentOrder.is_to_electronic_invoice()          
          for(let i =0; i++; i<2000) console.log("Validando facturacion ELECTRONICA")
          if (!to_electronic_invoice) {
              this.env.services.popup.add(ErrorPopup, {
                  title: 'Debe Seleccionar Factura y Factura electrónica',
                  body: 'Por favor seleccione en el panel derecho Factura y Factura electrónica',
              });
          } else {
              return super.validateOrder(...arguments);
          }
      },
  });