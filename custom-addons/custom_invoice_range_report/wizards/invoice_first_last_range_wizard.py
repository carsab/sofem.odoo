# custom_invoice_range_report/wizards/invoice_first_last_range_wizard.py
import base64
import csv
import io
from datetime import date, datetime, time
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class InvoiceFirstLastRangeWizard(models.TransientModel):
    # ... (Mantén _name, _description, campos, computes, constrains como estaban) ...
    _name = 'invoice.first.last.range.wizard'
    _description = 'Asistente Reporte Primera/Última Factura por Rango'

    def _get_default_date_start(self):
        today = fields.Date.context_today(self)
        return today.replace(day=1)

    def _get_default_date_end(self):
        return fields.Date.context_today(self)

    date_start = fields.Date(
        string="Fecha Inicio",
        required=True,
        default=_get_default_date_start
    )
    date_end = fields.Date(
        string="Fecha Fin",
        required=True,
        default=_get_default_date_end
    )
    report_line_ids = fields.One2many(
        'invoice.first.last.range.report.line',
        'wizard_id',
        string="Líneas de Reporte"
    )
    csv_filename = fields.Char(string='Nombre archivo CSV', compute='_compute_csv_filename', readonly=True)
    csv_file = fields.Binary(string='Archivo CSV', readonly=True)


    @api.depends('date_start', 'date_end')
    def _compute_csv_filename(self):
        for wizard in self:
            ds = wizard.date_start.strftime('%Y%m%d') if wizard.date_start else 'nodate'
            de = wizard.date_end.strftime('%Y%m%d') if wizard.date_end else 'nodate'
            wizard.csv_filename = f'reporte_facturas_{ds}_{de}.csv'

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for record in self:
            if record.date_start and record.date_end and record.date_start > record.date_end:
                raise UserError(_("La fecha de inicio no puede ser posterior a la fecha de fin."))


    # --- VERSIÓN CON SQL DIRECTO Y FILTRO DE COMPAÑÍA ACTIVA ---
    def _prepare_report_data(self):
        """
        Calcula los datos del reporte usando SQL directo,
        filtrando por las compañías activas del usuario.
        Devuelve una lista de diccionarios.
        """
        self.ensure_one()
        cr = self.env.cr # Obtener el cursor de la base de datos

        # Obtener los IDs de las compañías permitidas para el usuario actual.
        # Es crucial convertirlo a tupla para usarlo como parámetro en la consulta SQL.
        allowed_company_ids = tuple(self.env.companies.ids)

        # Si por alguna razón no hay compañías permitidas, retornar vacío para evitar errores SQL.
        if not allowed_company_ids:
             return []

        # Parámetros para las consultas SQL (previene inyección SQL)
        # Añadimos allowed_company_ids a los parámetros.
        params = (self.date_start, self.date_end, allowed_company_ids)

        # --- Consulta para obtener la PRIMERA factura de cada grupo ---
        # Añadido: AND am.company_id IN %s
        sql_first = """
            SELECT DISTINCT ON (am.journal_id, am.invoice_user_id)
                   am.journal_id,
                   am.invoice_user_id,
                   am.id AS first_invoice_id,
                   am.name AS first_invoice_name
            FROM account_move am
            WHERE am.move_type = 'out_invoice'
              AND am.state = 'posted'
              AND am.invoice_date >= %s
              AND am.invoice_date <= %s
              AND am.company_id IN %s  -- Filtro por compañía(s) activa(s)
            ORDER BY am.journal_id,
                     am.invoice_user_id,
                     am.invoice_date ASC,
                     am.name ASC,
                     am.id ASC;
        """
        cr.execute(sql_first, params)
        first_invoice_results = cr.dictfetchall()

        # --- Consulta para obtener la ÚLTIMA factura de cada grupo ---
        # Añadido: AND am.company_id IN %s
        sql_last = """
            SELECT DISTINCT ON (am.journal_id, am.invoice_user_id)
                   am.journal_id,
                   am.invoice_user_id,
                   am.id AS last_invoice_id,
                   am.name AS last_invoice_name
            FROM account_move am
            WHERE am.move_type = 'out_invoice'
              AND am.state = 'posted'
              AND am.invoice_date >= %s
              AND am.invoice_date <= %s
              AND am.company_id IN %s  -- Filtro por compañía(s) activa(s)
            ORDER BY am.journal_id,
                     am.invoice_user_id,
                     am.invoice_date DESC,
                     am.name DESC,
                     am.id DESC;
        """
        cr.execute(sql_last, params)
        last_invoice_results = cr.dictfetchall()

        # --- Combinar resultados y obtener nombres relacionados (SIN CAMBIOS EN ESTA PARTE) ---
        if not first_invoice_results:
            return []

        combined_data = {}
        journal_ids = set()
        user_ids = set()

        for res in first_invoice_results:
            j_id = res.get('journal_id')
            u_id = res.get('invoice_user_id')
            if j_id: journal_ids.add(j_id)
            if u_id: user_ids.add(u_id)
            group_key = (j_id or 0, u_id or 0)
            combined_data[group_key] = {
                'journal_id': j_id, 'user_id': u_id,
                'first_invoice_id': res.get('first_invoice_id'),
                'first_invoice_name': res.get('first_invoice_name'),
                'last_invoice_id': None, 'last_invoice_name': None,
            }

        for res in last_invoice_results:
            j_id = res.get('journal_id')
            u_id = res.get('invoice_user_id')
            group_key = (j_id or 0, u_id or 0)
            if group_key in combined_data:
                combined_data[group_key]['last_invoice_id'] = res.get('last_invoice_id')
                combined_data[group_key]['last_invoice_name'] = res.get('last_invoice_name')

        journal_names = {j.id: j.display_name for j in self.env['account.journal'].browse(list(journal_ids))}
        user_names = {u.id: u.display_name for u in self.env['res.users'].browse(list(user_ids))}

        report_data = []
        for group_key, data in combined_data.items():
            j_id = data['journal_id']
            u_id = data['user_id']
            report_data.append({
                'journal_name': journal_names.get(j_id, _('N/A')) if j_id else _('N/A'),
                'journal_id': j_id,
                'user_name': user_names.get(u_id, _('(Sin Vendedor)')) if u_id else _('(Sin Vendedor)'),
                'user_id': u_id,
                'first_invoice_name': data['first_invoice_name'],
                'first_invoice_id': data['first_invoice_id'],
                'last_invoice_name': data['last_invoice_name'],
                'last_invoice_id': data['last_invoice_id'],
            })

        report_data.sort(key=lambda x: (x['journal_name'], x['user_name']))
        return report_data
    # --- FIN DE LA VERSIÓN CON SQL DIRECTO Y FILTRO DE COMPAÑÍA ACTIVA ---


    # --- MÉTODOS action_view_report, action_print_pdf, etc. (SIN CAMBIOS) ---
    # Estos métodos simplemente llaman a _prepare_report_data(),
    # por lo que usarán automáticamente la nueva lógica con filtro de compañía.
    # ... (copiar los métodos action_view_report, action_print_pdf, action_print_xlsx, action_print_csv tal como estaban en la respuesta anterior) ...
    def action_view_report(self):
        """ Muestra los resultados en pantalla (Tree View) - SIN CAMBIOS """
        self.ensure_one()
        ReportLine = self.env['invoice.first.last.range.report.line']
        self.report_line_ids.unlink() # Limpiar resultados anteriores
        report_data = self._prepare_report_data() # Llama a la nueva versión SQL

        if not report_data:
            raise UserError(_("No se encontraron facturas para el rango de fechas seleccionado."))

        lines_vals = []
        for data in report_data:
            lines_vals.append({
                'wizard_id': self.id,
                'journal_id': data['journal_id'],
                'user_id': data['user_id'],
                'first_invoice_id': data['first_invoice_id'],
                'first_invoice_name': data['first_invoice_name'],
                'last_invoice_id': data['last_invoice_id'],
                'last_invoice_name': data['last_invoice_name'],
            })
        ReportLine.create(lines_vals)

        action = self.env['ir.actions.actions']._for_xml_id('custom_invoice_range_report.action_invoice_first_last_range_report_lines_view')
        action['domain'] = [('wizard_id', '=', self.id)]
        return action


    def action_print_pdf(self):
        """ Genera el reporte PDF - SIN CAMBIOS """
        self.ensure_one()
        report_data = self._prepare_report_data() # Llama a la nueva versión SQL
        if not report_data:
            raise UserError(_("No hay datos para generar el PDF."))
        data_for_report = {
            'report_data': report_data,
            'date_start': self.date_start.strftime('%d/%m/%Y'),
            'date_end': self.date_end.strftime('%d/%m/%Y'),
        }
        return self.env.ref('custom_invoice_range_report.action_report_invoice_first_last_range_pdf').report_action(self, data=data_for_report)

    def action_print_xlsx(self):
        """ Genera el reporte XLSX - SIN CAMBIOS """
        self.ensure_one()
        report_data = self._prepare_report_data() # Llama a la nueva versión SQL
        if not report_data:
            raise UserError(_("No hay datos para generar el XLSX."))
        data_for_report = {
            'report_data': report_data,
            'date_start': self.date_start.strftime('%d/%m/%Y'),
            'date_end': self.date_end.strftime('%d/%m/%Y'),
            'wizard_id': self.id
        }
        return self.env.ref('custom_invoice_range_report.action_report_invoice_first_last_range_xlsx').report_action(self, data=data_for_report)

    def action_print_csv(self):
        """ Genera y permite descargar el reporte CSV - SIN CAMBIOS """
        self.ensure_one()
        report_data = self._prepare_report_data() # Llama a la nueva versión SQL
        if not report_data:
            raise UserError(_("No hay datos para generar el CSV."))
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_ALL)
        header = [
            _("Punto de Venta (Diario)"), _("Vendedor"), _("Nro. Primera Factura"),
            _("ID Primera Factura"), _("Nro. Última Factura"), _("ID Última Factura")
        ]
        writer.writerow(header)
        for row in report_data:
            writer.writerow([
                row.get('journal_name', ''), row.get('user_name', ''),
                row.get('first_invoice_name', ''), row.get('first_invoice_id', ''),
                row.get('last_invoice_name', ''), row.get('last_invoice_id', '')
            ])
        csv_data = base64.b64encode(output.getvalue().encode('utf-8'))
        output.close()
        self.write({'csv_file': csv_data})
        return {
            'type': 'ir.actions.act_window', 'res_model': self._name,
            'res_id': self.id, 'view_mode': 'form', 'target': 'new',
        }