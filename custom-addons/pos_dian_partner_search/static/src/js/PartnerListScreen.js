/** @odoo-module **/

import { PartnerListScreen } from "@point_of_sale/app/screens/partner_list/partner_list";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { DianSearchPopup } from "@pos_dian_partner_search/js/DianSearchPopup";
import { Component } from "@odoo/owl";

patch(PartnerListScreen.prototype, {
    setup() {
        super.setup();
        this.popup = useService("popup");
        this.orm = useService("orm");
        this.notification = useService("notification");
        
        console.log("POS DIAN Partner Search loaded successfully");
        console.log("DianSearchPopup available:", !!DianSearchPopup);
    },

    /**
     * Override del método updatePartnerList para incluir búsqueda DIAN
     */
    async updatePartnerList(event) {
        const searchValue = event?.target?.value?.trim() || '';
        
        if (!searchValue) {
            return super.updatePartnerList(event);
        }

        this.state.query = searchValue;
        const isNumericSearch = /^\d+$/.test(searchValue);
        
        if (event?.key === 'Enter' && isNumericSearch && searchValue.length >= 6) {
            event.preventDefault();
            await this.searchPartnerWithDian(searchValue);
            return;
        }
        
        return super.updatePartnerList(event);
    },

    /**
     * Busca un asociado usando el servicio DIAN
     */
    async searchPartnerWithDian(identificationNumber) {
        try {
            // Usar servicio directamente desde env como fallback
            const notif = this.notification || this.env.services.notification;
            
            notif.add(_t("Buscando en DIAN..."), {
                type: "info",
            });

            const identificationType = 'national_citizen_id';
            const ormService = this.orm || this.env.services.orm;

            const result = await ormService.call(
                'res.partner',
                'search_from_dian',
                [identificationType, identificationNumber],
            );

            if (result && result.id) {
                // Recargar partners desde la base de datos
                const partnerData = await ormService.searchRead(
                    'res.partner',
                    [['id', '=', result.id]],
                    ['id', 'name', 'vat', 'email', 'phone', 'street', 'city', 'country_id', 'dian_search_attempted']
                );
                
                if (partnerData && partnerData.length > 0) {
                    // Actualizar la lista de partners con el nuevo
                    this.state.partners = partnerData;
                    notif.add(
                        _t("Asociado encontrado y creado desde DIAN: %s", partnerData[0].name),
                        { type: "success" }
                    );
                } else {
                    notif.add(
                        _t("Asociado creado desde DIAN exitosamente"),
                        { type: "success" }
                    );
                    // Recargar la búsqueda
                    await super.updatePartnerList({ target: { value: identificationNumber } });
                }
            } else {
                notif.add(
                    _t("Asociado no encontrado en DIAN, buscando localmente..."),
                    { type: "warning" }
                );
                await super.updatePartnerList({ target: { value: identificationNumber } });
            }
        } catch (error) {
            console.error('Error searching partner in DIAN:', error);
            const notif = this.notification || this.env.services.notification;
            notif.add(
                _t("Error buscando en DIAN. Buscando localmente..."),
                { type: "danger" }
            );
            await super.updatePartnerList({ target: { value: identificationNumber } });
        }
    },

    /**
     * Abre diálogo de búsqueda avanzada - CORREGIDO
     */
    async openAdvancedSearch() {
        console.log("=== openAdvancedSearch called ===");
        
        // CORRECCIÓN: Usar this.env.services.popup directamente en lugar de this.popup
        const popupService = this.popup || this.env.services.popup;
        const notificationService = this.notification || this.env.services.notification;
        
        console.log("popupService:", popupService);
        console.log("DianSearchPopup:", DianSearchPopup);

        if (!popupService) {
            console.error("Popup service not available!");
            alert("Error: Servicio de popup no disponible. Por favor recargue la página.");
            return;
        }

        if (!DianSearchPopup) {
            console.error("DianSearchPopup not loaded!");
            notificationService.add(
                _t("Error: Módulo de búsqueda DIAN no disponible"),
                { type: "danger" }
            );
            return;
        }

        try {
            console.log("Opening popup...");
            const { confirmed, payload } = await popupService.add(DianSearchPopup, {
                title: _t("Búsqueda Avanzada DIAN"),
            });

            console.log("Popup closed. Confirmed:", confirmed, "Payload:", payload);

            if (confirmed && payload) {
                await this.searchWithIdentification(
                    payload.identificationType,
                    payload.identificationNumber
                );
            }
        } catch (error) {
            console.error("Error opening popup:", error);
            notificationService.add(
                _t("Error abriendo búsqueda avanzada: %s", error.message),
                { type: "danger" }
            );
        }
    },

    /**
     * Busca con tipo de identificación específico
     */
    async searchWithIdentification(identificationType, identificationNumber) {
        try {
            const notif = this.notification || this.env.services.notification;
            const ormService = this.orm || this.env.services.orm;
            
            notif.add(_t("Buscando en DIAN..."), {
                type: "info",
            });

            const result = await ormService.call(
                'res.partner',
                'search_from_dian',
                [identificationType, identificationNumber],
            );

            if (result && result.id) {
                // Recargar el partner desde la base de datos
                const partnerData = await ormService.searchRead(
                    'res.partner',
                    [['id', '=', result.id]],
                    ['id', 'name', 'vat', 'email', 'phone', 'street', 'city', 'country_id', 'dian_search_attempted']
                );
                
                if (partnerData && partnerData.length > 0) {
                    this.state.partners = partnerData;
                    this.state.query = partnerData[0].name;
                    
                    notif.add(
                        _t("Asociado encontrado: %s", partnerData[0].name),
                        { type: "success" }
                    );
                } else {
                    notif.add(
                        _t("Asociado creado desde DIAN exitosamente"),
                        { type: "success" }
                    );
                    this.state.partners = [];
                }
            } else {
                notif.add(_t("Asociado no encontrado en DIAN"), {
                    type: "warning",
                });
                this.state.partners = [];
            }
        } catch (error) {
            console.error('Error in advanced DIAN search:', error);
            const notif = this.notification || this.env.services.notification;
            notif.add(
                _t("Error: %s", error.message || error.data?.message || error),
                { type: "danger" }
            );
        }
    }
});