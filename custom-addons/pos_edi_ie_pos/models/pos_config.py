# -*- coding: utf-8 -*-
from odoo import fields, models

class PosConfig(models.Model):
    _inherit = 'pos.config'

    x_l10n_co_edi_online_validation = fields.Boolean(
        string='Validación Online DIAN',
        help="Si está marcado, la factura electrónica se validará en línea con la DIAN antes de la impresión en este Punto de Venta.",
        default=False 
    )

    # Es importante asegurarse de que este nuevo campo se carga en la interfaz del PoS.
    # Odoo 16+ lo hace automáticamente para campos de pos.config si están en la vista,
    # pero si no, o para versiones anteriores, podrías necesitar algo como:
    def _get_pos_ui_pos_config_data(self, params):
        # En Odoo 17, los campos de pos.config generalmente se cargan si están en una vista
        # y accesibles. Si necesitas forzarlo o añadir más lógica:
        config_data = super()._get_pos_ui_pos_config_data(params)
        config_data.update({
            'x_l10n_co_edi_online_validation': self.x_l10n_co_edi_online_validation,
        })
        return config_data

    # Si el método anterior no existe o no es el adecuado para Odoo 17 en tu contexto específico,
    # verifica la documentación o ejemplos de cómo se cargan los campos de `pos.config`
    # en el PoS. A menudo, simplemente añadirlo a la vista es suficiente y se accede
    # vía `this.pos.config.x_l10n_co_edi_online_validation` en JS.
    # Para Odoo 17, los campos de `pos.config` se cargan en `PosStore.config`
    # si son leídos por el cliente (`this.env.services.pos.config`).
    # No se requiere un método especial como _get_pos_ui_pos_config_data usualmente.
    # Los campos se pueden añadir a través de `get_pos_ui_config_fields_to_read`
    # si no se cargan automáticamente.

    # Revisando la fuente de Odoo 17 `point_of_sale/models/pos_config.py`:
    # El método `get_pos_ui_config_fields_to_read` es el lugar correcto para asegurar
    # que el campo es leído por el cliente PoS.
    @property
    def get_pos_ui_config_fields_to_read(self):
        """
        Devuelve la lista de campos de `pos.config` que deben ser leídos por la UI del PoS.
        """
        fields_to_read = super().get_pos_ui_config_fields_to_read
        fields_to_read.append('x_l10n_co_edi_online_validation')
        return fields_to_read