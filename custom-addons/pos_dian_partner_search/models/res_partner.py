# -*- coding: utf-8 -*-
# Módulo: POS DIAN Partner Search
# Descripción: Integra búsqueda DIAN en la ventana de búsqueda de asociados del POS

import json
import logging
import re

import requests
from odoo import fields, models, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    dian_search_attempted = fields.Boolean("DIAN search attempted", default=False, copy=False)

    def _edi_sanitize_vat(self, vat, type_document_identification_id):
        """Sanitiza VAT según el tipo de documento de identificación"""
        sanitize_vat = vat and re.sub(r'\W+', '', vat).upper() or False
        if sanitize_vat:
            if type_document_identification_id in (1, 2, 3, 4, 5, 6, 10, 24, 38):
                id_number = ''.join([i for i in sanitize_vat if i.isdigit()])
            else:
                id_number = sanitize_vat

            if type_document_identification_id == 6:
                return id_number[:-1]
            else:
                return id_number
        else:
            return None

    def _get_dian_data(self, id_code, id_number):
        """Obtiene datos del asociado desde la API DIAN"""
        try:
            company = self.env.company
            
            if not hasattr(company, 'api_key') or not company.api_key:
                raise UserError(_("You must configure a token in company settings"))

            api_url = self.env['ir.config_parameter'].sudo().get_param(
                'jorels.edipo.api_url',
                'https://edipo.jorels.com'
            )
            api_url = api_url + "/acquirer/" + str(id_code) + "/" + str(id_number)

            params = {'token': company.api_key}
            headers = {
                "accept": "application/json",
                "Content-Type": "application/json"
            }

            response = requests.post(
                api_url,
                json.dumps({}),
                headers=headers,
                params=params,
                timeout=10
            ).json()

            _logger.debug('DIAN API Response: %s', response)

            if 'detail' in response:
                raise UserError(response['detail'])
            if 'message' in response and response['message'] is not None:
                if response['message'] in ('Unauthenticated.', ''):
                    raise UserError(_("Authentication error with the DIAN API"))
                else:
                    errors_msg = ''
                    if 'errors' in response:
                        errors_msg = '/ errors: ' + str(response['errors'])
                    raise UserError(response['message'] + errors_msg)

            return response

        except Exception as e:
            _logger.error("Failed to query DIAN: %s", e)
            raise

    def _get_type_document_identification_id(self, document_code):
        """Obtiene el ID del tipo de identificación según el código del documento"""
        document_type_mapping = {
            'rut': 6,
            'national_citizen_id': 3,
            'civil_registration': 1,
            'id_card': 2,
            'foreign_colombian_card': 4,
            'foreign_resident_card': 5,
            'passport': 7,
            'PEP': 24,
            'foreign_id_card': 8,
            'external_id': 9,
            'niup_id': 10,
            'id_document': 3,
            'PPT': 38,
        }
        return document_type_mapping.get(document_code)

    def _get_l10n_latam_identification_type(self, document_code):
        """Obtiene el registro de l10n_latam.identification.type"""
        return self.env['l10n_latam.identification.type'].search([
            ('l10n_co_document_code', '=', document_code)
        ], limit=1)

    def _format_colombian_name(self, name):
        """Formatea el nombre colombiano: primeros dos palabras son apellidos"""
        words = name.strip().split()

        if len(words) < 2:
            return name

        if len(words) == 2:
            return "{}, {}".format(words[0], words[1])

        last_names = " ".join(words[:2])
        first_names = " ".join(words[2:])

        return "{}, {}".format(last_names, first_names)

    def _create_partner_from_dian(self, document_code, id_number, dian_response):
        """Crea un nuevo asociado con los datos obtenidos de DIAN"""
        try:
            company = self.env.company
            country_co = self.env['res.country'].search([('code', '=', 'CO')], limit=1)

            # Obtener el tipo de documento
            l10n_latam_type = self._get_l10n_latam_identification_type(document_code)
            
            if not l10n_latam_type:
                raise UserError(_("Identification type not found for code: %s") % document_code)

            # Determinar si es compañía o persona
            is_company_type = document_code in ('rut', 'niup_id')
            
            # Formatear el nombre
            raw_name = dian_response.get('name', '').title()
            formatted_name = raw_name if is_company_type else self._format_colombian_name(raw_name)

            # Preparar datos del asociado
            partner_vals = {
                'name': formatted_name,
                'vat': id_number,
                'l10n_latam_identification_type_id': l10n_latam_type.id,
                'country_id': country_co.id if country_co else False,
                'is_company': is_company_type,
                'dian_search_attempted': True,
                'customer_rank': 1,  # Marcar como cliente
            }

            # Email solo si no es el genérico
            email = dian_response.get('email', '')
            if email and email != 'sininformacion@correo.com':
                partner_vals['email'] = email
                partner_vals['email_edi'] = email

            # Agregar datos de la compañía si están disponibles
            if hasattr(company, 'state_id') and company.state_id:
                partner_vals['state_id'] = company.state_id.id

            if hasattr(company, 'city') and company.city:
                partner_vals['city'] = company.city

            if hasattr(company, 'municipality_id') and company.municipality_id:
                partner_vals['municipality_id'] = company.municipality_id.id

            # Régimen y responsabilidad fiscal por defecto
            if hasattr(company, 'type_regime_id'):
                partner_vals['type_regime_id'] = 2  # Régimen simplificado por defecto

            if hasattr(company, 'type_liability_id'):
                partner_vals['type_liability_id'] = 29  # R-99-PN por defecto

            # Crear el nuevo asociado
            new_partner = self.create(partner_vals)
            _logger.info("New partner created from DIAN: ID=%s, Name=%s", new_partner.id, new_partner.name)
            
            # Crear mensaje en el chatter
            new_partner.message_post(
                body=_("Partner created automatically from DIAN search.<br/>Identification: %s") % id_number
            )
            
            return new_partner

        except Exception as e:
            _logger.error("Failed to create partner from DIAN data: %s", e)
            raise

    @api.model
    def search_from_dian(self, identification_type_code, identification_number):
        """
        Busca un asociado localmente y si no existe, lo obtiene de DIAN
        
        Args:
            identification_type_code: Código del tipo de identificación
            identification_number: Número de identificación
            
        Returns:
            Dict con {'id': partner_id} si lo encuentra o crea, False si no
        """
        try:
            company = self.env.company
            
            # Validar que el módulo DIAN esté habilitado
            if not hasattr(company, 'ei_enable') or not company.ei_enable:
                _logger.warning("EDI module not enabled in company")
                return False

            # Obtener el tipo de documento de identificación
            type_id = self._get_type_document_identification_id(identification_type_code)
            if not type_id:
                raise UserError(_("Invalid identification type: %s") % identification_type_code)

            # Sanitizar el número de identificación
            sanitized_id = self._edi_sanitize_vat(identification_number, type_id)
            if not sanitized_id:
                raise UserError(_("Invalid identification number"))

            # Validar que no sea el consumidor final por defecto
            if sanitized_id == '222222222222':
                return False

            _logger.info("Searching partner with VAT: %s", sanitized_id)

            # Buscar localmente por VAT sanitizado
            existing_partner = self.search([
                ('vat', '=', sanitized_id),
                '|',
                ('company_id', '=', False),
                ('company_id', '=', company.id)
            ], limit=1)

            if existing_partner:
                _logger.info("Partner found locally: ID=%s, Name=%s", existing_partner.id, existing_partner.name)
                return {'id': existing_partner.id}

            # No existe localmente, buscar en DIAN
            _logger.info("Partner not found locally, searching in DIAN")
            dian_response = self._get_dian_data(type_id, sanitized_id)

            if not dian_response or not dian_response.get('name'):
                _logger.warning("No valid response from DIAN for ID: %s", sanitized_id)
                return False

            # Crear el nuevo asociado con los datos de DIAN
            new_partner = self._create_partner_from_dian(
                identification_type_code,
                sanitized_id,
                dian_response
            )
            
            return {'id': new_partner.id}

        except UserError:
            raise
        except Exception as e:
            _logger.error("Error in search_from_dian: %s", e)
            raise UserError(_("Error searching partner in DIAN: %s") % str(e))

    @api.model
    def pos_search_partner(self, search_query=None, identification_type=None, identification_number=None):
        """
        Busca asociados para POS con opción de búsqueda DIAN
        
        Args:
            search_query: Búsqueda por nombre
            identification_type: Tipo de identificación
            identification_number: Número de identificación
        """
        
        company = self.env.company
        domain = [
            '|',
            ('company_id', '=', False),
            ('company_id', '=', company.id)
        ]

        # Si se proporciona tipo e número de identificación, buscar en DIAN
        if identification_type and identification_number:
            try:
                result = self.search_from_dian(identification_type, identification_number)
                if result and result.get('id'):
                    partner = self.browse(result['id'])
                    return partner.read(self._get_partner_fields())
                return []
            except Exception as e:
                _logger.warning("DIAN search failed: %s", e)
                # Continuar con búsqueda local
                pass

        # Búsqueda local
        if search_query:
            domain += [
                '|', '|', '|',
                ('name', 'ilike', search_query),
                ('vat', 'ilike', search_query),
                ('email', 'ilike', search_query),
                ('phone', 'ilike', search_query)
            ]

        partners = self.search(domain, limit=20)
        return partners.read(self._get_partner_fields())

    def _get_partner_fields(self):
        """Retorna los campos a devolver en búsquedas"""
        return [
            'id', 'name', 'vat', 'email', 'phone', 
            'city', 'country_id', 'l10n_latam_identification_type_id',
            'dian_search_attempted'
        ]