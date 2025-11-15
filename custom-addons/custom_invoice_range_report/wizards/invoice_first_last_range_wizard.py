# custom_invoice_range_report/wizards/invoice_first_last_range_wizard.py
import base64
import csv
import io
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class InvoiceFirstLastRangeWizard(models.TransientModel):
    _name = 'invoice.first.last.range.wizard'
    _description = 'Asistente Reporte Primera/Última Factura por Rango'

    def _get_default_date_start(self):
        return fields.Date.context_today(self).replace(day=1)

    def _get_default_date_end(self):
        return fields.Date.context_today(self)

    date_start = fields.Date(string="Fecha Inicio", required=True, default=_get_default_date_start)
    date_end = fields.Date(string="Fecha Fin", required=True, default=_get_default_date_end)
    report_line_ids = fields.One2many('invoice.first.last.range.report.line', 'wizard_id', string="Líneas de Reporte")
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

    def _prepare_report_data(self):
        self.ensure_one()
        cr = self.env.cr
        allowed_company_ids = tuple(self.env.companies.ids)
        if not allowed_company_ids:
             return []

        params = (self.date_start, self.date_end, allowed_company_ids)
        sql_first = """
            SELECT distinct on (journal_id, punto)
                   journal_id, punto, first_invoice_id, first_invoice_name
            FROM (
                SELECT am.journal_id,
                       coalesce((SELECT pc.name FROM pos_config pc
                                 JOIN pos_session ps ON ps.config_id = pc.id
                                 JOIN pos_order po ON po.session_id = ps.id
                                 WHERE po.account_move = am.id LIMIT 1), 'FACTURACION') as punto,
                       am.id as first_invoice_id, am.name as first_invoice_name, am.invoice_date
                FROM account_move am
                WHERE am.move_type = 'out_invoice' AND am.state = 'posted'
                  AND am.invoice_date >= %s AND am.invoice_date <= %s AND am.company_id IN %s
            ) as fact_orden
            ORDER BY journal_id, punto, invoice_date asc, first_invoice_name asc, first_invoice_id asc;
        """
        cr.execute(sql_first, params)
        first_invoice_results = cr.dictfetchall()
        sql_last = """
            SELECT distinct on (journal_id, punto)
                   journal_id, punto, last_invoice_id, last_invoice_name
            FROM (
                SELECT am.journal_id,
                       coalesce((SELECT pc.name FROM pos_config pc
                                 JOIN pos_session ps ON ps.config_id = pc.id
                                 JOIN pos_order po ON po.session_id = ps.id
                                 WHERE po.account_move = am.id LIMIT 1), 'FACTURACION') as punto,
                       am.id as last_invoice_id, am.name as last_invoice_name, am.invoice_date
                FROM account_move am
                WHERE am.move_type = 'out_invoice' AND am.state = 'posted'
                  AND am.invoice_date >= %s AND am.invoice_date <= %s AND am.company_id IN %s
            ) as fact_orden
            ORDER BY journal_id, punto, invoice_date desc, last_invoice_name desc, last_invoice_id desc;
        """
        cr.execute(sql_last, params)
        last_invoice_results = cr.dictfetchall()
        if not first_invoice_results: return []
        combined_data = {}
        journal_ids = set()
        for res in first_invoice_results:
            j_id, punto_name = res.get('journal_id'), res.get('punto')
            if j_id: journal_ids.add(j_id)
            group_key = (j_id or 0, punto_name or '')
            combined_data[group_key] = {
                'journal_id': j_id, 'pos_name': punto_name,
                'first_invoice_id': res.get('first_invoice_id'), 'first_invoice_name': res.get('first_invoice_name'),
                'last_invoice_id': None, 'last_invoice_name': None,
            }
        for res in last_invoice_results:
            j_id, punto_name = res.get('journal_id'), res.get('punto')
            group_key = (j_id or 0, punto_name or '')
            if group_key in combined_data:
                combined_data[group_key]['last_invoice_id'] = res.get('last_invoice_id')
                combined_data[group_key]['last_invoice_name'] = res.get('last_invoice_name')
        journal_names = {j.id: j.display_name for j in self.env['account.journal'].browse(list(journal_ids))}
        report_data = []
        for group_key, data in combined_data.items():
            j_id = data['journal_id']
            # Este diccionario contiene 'journal_name' a propósito para los reportes PDF/XLSX
            report_data.append({
                'journal_name': journal_names.get(j_id, _('N/A')) if j_id else _('N/A'),
                'journal_id': j_id,
                'pos_name': data['pos_name'],
                'first_invoice_name': data['first_invoice_name'], 'first_invoice_id': data['first_invoice_id'],
                'last_invoice_name': data['last_invoice_name'], 'last_invoice_id': data['last_invoice_id'],
            })
        report_data.sort(key=lambda x: (x['pos_name'], x['journal_name']))
        return report_data

    def action_view_report(self):
        self.ensure_one()
        self.report_line_ids.unlink()
        report_data = self._prepare_report_data()
        if not report_data:
            raise UserError(_("No se encontraron facturas para el rango de fechas seleccionado."))

        lines_vals = []
        for data in report_data:
            vals = {
                'wizard_id': self.id,
                'pos_name': data.get('pos_name'),
                'journal_id': data.get('journal_id'),
                'first_invoice_id': data.get('first_invoice_id'),
                'first_invoice_name': data.get('first_invoice_name'),
                'last_invoice_id': data.get('last_invoice_id'),
                'last_invoice_name': data.get('last_invoice_name'),
            }
            lines_vals.append(vals)

        action = self.env['ir.actions.actions']._for_xml_id('custom_invoice_range_report.action_invoice_first_last_range_report_lines_view')
        action['domain'] = [('wizard_id', '=', self.id)]
        return action

    def _get_report_common_data(self):
        report_data = self._prepare_report_data()
        if not report_data:
            raise UserError(_("No hay datos para generar el reporte."))
        return {
            'report_data': report_data,
            'date_start': self.date_start.strftime('%d/%m/%Y'),
            'date_end': self.date_end.strftime('%d/%m/%Y'),
        }

    def action_print_pdf(self):
        data = self._get_report_common_data()
        # Mapeamos 'pos_name' al nombre que espera la plantilla para no tener que cambiarla
        for row in data['report_data']:
            row['pos_config_name'] = row.get('pos_name')
        return self.env.ref('custom_invoice_range_report.action_report_invoice_first_last_range_pdf').report_action(self, data=data)

    def action_print_xlsx(self):
        data = self._get_report_common_data()
        return self.env.ref('custom_invoice_range_report.action_report_invoice_first_last_range_xlsx').report_action(self, data=data)

    def action_print_csv(self):
        report_data = self._prepare_report_data()
        if not report_data: raise UserError(_("No hay datos para generar el CSV."))
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_ALL)
        writer.writerow([_("Punto de Venta"), _("Diario"), _("Nro. Primera Factura"), _("ID Primera Factura"), _("Nro. Última Factura"), _("ID Última Factura")])
        for row in report_data:
            writer.writerow([
                row.get('pos_name', ''), row.get('journal_name', ''),
                row.get('first_invoice_name', ''), row.get('first_invoice_id', ''),
                row.get('last_invoice_name', ''), row.get('last_invoice_id', '')
            ])
        csv_data = base64.b64encode(output.getvalue().encode('utf-8'))
        output.close()
        self.write({'csv_file': csv_data})
        return {'type': 'ir.actions.act_window', 'res_model': self._name, 'res_id': self.id, 'view_mode': 'form', 'target': 'new'}
