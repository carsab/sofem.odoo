/** @odoo-module */

import { useService } from "@web/core/utils/hooks";
import { renderToElement } from "@web/core/utils/render";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
//import { formatCurrency } from "@web/core/currency";
//import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";

export class SaleDetailsButton extends Component {
    static template = "point_of_sale.SaleDetailsButton";
    static props = {
        data: Object,
        formatCurrency: Function,
    };
    setup() {
        super.setup(...arguments);
        this.pos = usePos();
        this.popup = useService("popup");
        this.orm = useService("orm");
        this.printer = useService("printer");
        this.hardwareProxy = useService("hardware_proxy");
    }

    async onClick() {
        // IMPROVEMENT: Perhaps put this logic in a parent component
        // so that for unit testing, we can check if this simple
        // component correctly triggers an event.
        const saleDetails = await this.orm.call(
            "report.point_of_sale.report_saledetails",
            "get_sale_details",
            [false, false, false, [this.pos.pos_session.id]]
        );
        console.log("IMPRESION TIRILLA :::::>", this.pos.pos_session.id)
        saleDetails.headerData = this.pos.getReceiptHeaderData()

        console.log("DATA TIRILLA:::::>", saleDetails)
        const report = renderToElement(
            "point_of_sale.SaleDetailsReport",
            Object.assign({}, saleDetails, {
                date: new Date().toLocaleString(),
                pos: this.pos,
                formatCurrency: this.env.utils.formatCurrency,
            })
        );
        console.log("RENDER TIRILLA:::::>", report)
        let rta = this.printer.printHtml(report, { webPrintFallback: true })
        console.log("Impresión detalle de ventas en tirilla", rta)
    }

    async printReport(report) {
        const isPrinted = await this.printer.print(
            report,
            {
                data: report,
                formatCurrency: this.env.utils.formatCurrency,
            },
            { webPrintFallback: true }
        );
    }
}
