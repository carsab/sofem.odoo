/** @odoo-module **/

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { useState } from "@odoo/owl";

export class DianSearchPopup extends AbstractAwaitablePopup {
    static template = "pos_dian_partner_search.DianSearchPopup";
    static defaultProps = {
        confirmText: _t("Buscar"),
        cancelText: _t("Cancelar"),
        title: _t("Búsqueda Avanzada DIAN"),
    };

    setup() {
        super.setup();
        this.state = useState({
            identificationType: 'national_citizen_id',
            identificationNumber: '',
        });

        this.identificationTypes = [
            { code: 'civil_registration', name: _t('Registro Civil') },
            { code: 'id_card', name: _t('Tarjeta de Identidad') },
            { code: 'national_citizen_id', name: _t('Cédula de Ciudadanía') },
            { code: 'foreign_colombian_card', name: _t('Tarjeta de Extranjería') },
            { code: 'foreign_resident_card', name: _t('Cédula de Extranjería') },
            { code: 'rut', name: _t('RUT') },
            { code: 'passport', name: _t('Pasaporte') },
            { code: 'foreign_id_card', name: _t('Documento Extranjero') },
            { code: 'external_id', name: _t('ID Externo') },
            { code: 'niup_id', name: _t('NIUP') },
            { code: 'PEP', name: _t('PEP') },
            { code: 'PPT', name: _t('PPT') },
        ];
    }

    onChangeType(ev) {
        this.state.identificationType = ev.target.value;
    }

    onChangeNumber(ev) {
        this.state.identificationNumber = ev.target.value;
    }

    getPayload() {
        if (!this.state.identificationNumber || this.state.identificationNumber.trim() === '') {
            return null;
        }

        return {
            identificationType: this.state.identificationType,
            identificationNumber: this.state.identificationNumber.trim(),
        };
    }

    confirm() {
        const payload = this.getPayload();
        if (payload) {
            super.confirm();
        }
    }
}