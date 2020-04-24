# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError,UserError
from datetime import datetime, timedelta
#from xml.sax.saxutils import escape
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

import xmltodict

import base64
import zipfile
import io
import calendar

from suds.client import Client
import random
import pdb


class XmlImportWizard(models.TransientModel):
    _inherit = 'xml.import.wizard'
    
    sat_validation = fields.Boolean(string='Validar en SAT',
        default=False)
    invoice_type = fields.Selection(
        [('out_invoice','Cliente'),
        ('in_invoice','Proveedor')],
        string='Tipo de factura',
        required=False,
        default=False)
    line_account_id = fields.Many2one('account.account',
        string='Cuenta de linea',
        required=False,
        help='Si la empresa no tiene definida una cuenta de importacion xml por defecto, se usara esta')
    invoice_account_id = fields.Many2one('account.account',
        string='Cuenta de Factura',
        required=False)
    journal_id = fields.Many2one('account.journal',
        string='Diario',
        required=False)
    payment_journal_id = fields.Many2one('account.journal',
        string='Banco de pago', required=False, domain="[('type','=','bank')]")
    
    ### Cliente ##########################################
    cuenta_cobrar_cliente_id = fields.Many2one('account.account',
        string='Cuenta por Cobrar Clientes',
        required=True, default=lambda self: self.env['account.account'].search([('code','=','105.01.01'),('company_id','=',self.env.user.company_id.id)]))
    cuenta_ingreso_cliente_id = fields.Many2one('account.account',
        string='Cuenta de Ingresos Clientes',
        required=True, default=lambda self: self.env['account.account'].search([('code','=','401.01.01'),('company_id','=',self.env.user.company_id.id)]))
    line_analytic_account_customer_id = fields.Many2one('account.analytic.account', 
        string='Cuenta analitica de linea',
        required=False)
    payment_term_customer_id = fields.Many2one(
        'account.payment.term',
        string='Plazo de pago',
        help='Se utilizara este plazo de pago para las empresas creadas automaticamente, '+\
        '\n si no se especifica, se usara el de 15 dias'
        )
    user_customer_id = fields.Many2one('res.users',
        string='Representante Comercial')
    team_customer_id = fields.Many2one('crm.team',
        string='Equipo de ventas')
    warehouse_customer_id = fields.Many2one('stock.warehouse', string='Almacén',
        help='Necesario para crear el mov. de almacén')
    journal_customer_id = fields.Many2one('account.journal',
        string='Diario Clientes',
        required=True, compute="_set_none")
    def _set_none(self):
        pass
    payment_journal_customer_id = fields.Many2one('account.journal',
        string='Banco de pago', domain="[('type','=','bank')]")
    line_analytic_tag_customer_ids = fields.Many2many('account.analytic.tag', 
        string='Etiquetas analíticas',
        required=False)
    invoice_status_customer = fields.Selection([('draft','Borrador'),('abierta','Abierta'),('pagada','Pagada')], string='Subir en estatus')
    invoice_payment_type_customer = fields.Selection([('fecha_factura','Con  la misma fecha de la factura'),('fecha_fin_mes','Con la fecha de final del mes'),('fecha_especifica','Con alguna fecha específica')], string='Fecha de pago')
    invoice_date_customer = fields.Date(string='Fecha')
    payment_method_customer = fields.Many2one('l10n_mx_edi.payment.method', string='Forma de pago')
    usage_customer = fields.Selection([
        ('G01', 'Adquisición de mercancías'),
        ('G02', 'Devoluciones, descuentos o bonificaciones'),
        ('G03', 'Gastos en general'),
        ('I01', 'Construcciones'),
        ('I02', 'Mobilario y equipo de oficina por inversiones'),
        ('I03', 'Equipo de transporte'),
        ('I04', 'Equipo de cómputo y accesorios'),
        ('I05', 'Dados, troqueles, moldes, matrices y herramental'),
        ('I06', 'Comunicaciones telefónicas'),
        ('I07', 'Comunicaciones satelitales'),
        ('I08', 'Otra maquinaria y equipo'),
        ('D01', 'Honorarios médicos, dentales y gastos hospitalarios'),
        ('D02', 'Gastos médicos por incapacidad o discapacidad'),
        ('D03', 'Gastos funerales'),
        ('D04', 'Donativos'),
        ('D05', 'Intereses reales efectivamente pagados por créditos hipotecarios (casa habitación)'),
        ('D06', 'Aportaciones voluntarias al SAR'),
        ('D07', 'Primas por seguros de gastos médicos'),
        ('D08', 'Gastos de transportación escolar obligatoria'),
        ('D09', 'Depósitos en cuentas para el ahorro, primas que tengan como base planes de pensiones'),
        ('D10', 'Pagos por servicios educativos (colegiaturas)'),
        ('P01', 'Por definir'),
    ], 'Uso', default='P01',
        help='Used in CFDI 3.3 to express the key to the usage that will '
        'gives the receiver to this invoice. This value is defined by the '
        'customer. \nNote: It is not cause for cancellation if the key set is '
        'not the usage that will give the receiver of the document.')
    
    ### Proveedor #############################
    cuenta_pagar_proveedor_id = fields.Many2one('account.account',
        string='Cuenta por Pagar Proveedores',
        required=True, default=lambda self: self.env['account.account'].search([('code','=','201.01.01'),('company_id','=',self.env.user.company_id.id)]))
    cuenta_gasto_proveedor_id = fields.Many2one('account.account',
        string='Cuenta de Gastos de Proveedor',
        required=True, default=lambda self: self.env['account.account'].search([('code','=','601.84.01'),('company_id','=',self.env.user.company_id.id)]))
    line_analytic_account_provider_id = fields.Many2one('account.analytic.account', 
        string='Etiquetas analíticas', required=False)
    payment_term_provider_id = fields.Many2one(
        'account.payment.term',
        string='Plazo de pago',
        help='Se utilizara este plazo de pago para las empresas creadas automaticamente, '+\
        '\n si no se especifica, se usara el de 15 dias'
        )
    user_provider_id = fields.Many2one('res.users',
        string='Comprador',)
    warehouse_provider_id = fields.Many2one('stock.warehouse', string='Almacén', 
        help='Necesario para crear el mov. de almacén', required=False)
    journal_provider_id = fields.Many2one('account.journal',
        string='Diario Proveedores',
        required=False, default=lambda self: self.env['account.journal'].search([('name','=','PROVEEDORES - Facturas'),('company_id','=',self.env.user.company_id.id)]))
    payment_journal_provider_id = fields.Many2one('account.journal',
        string='Banco de pago', domain="[('type','=','bank')]")
    line_analytic_tag_provider_ids = fields.Many2many('account.analytic.tag', 
        string='Etiquetas analíticas',
        required=False)
    invoice_status_provider = fields.Selection([('draft','Borrador'),('abierta','Abierta'),('pagada','Pagada')], string='Subir en estatus', required=False)
    invoice_payment_type_provider = fields.Selection([('fecha_factura','Con  la misma fecha de la factura'),('fecha_fin_mes','Con la fecha de final del mes'),('fecha_especifica','Con alguna fecha específica')], string='Fecha de pago')
    invoice_date_provider = fields.Date(string='Fecha')
    ##############################
    
    @api.onchange('invoice_status_customer')
    def _onchange_invoice_status_customer(self):
        if not self.invoice_status_customer:
            self.invoice_payment_type_customer = False
            self.invoice_date_provider = False
    
    @api.onchange('invoice_type','company_id')
    def _onchange_invoice_type(self):
        pass
        
        
    @api.onchange('uploaded_file')
    def onchnage_uploaded_file(self):
        if self.uploaded_file:
            file_ext = self.get_file_ext(self.filename)
            if file_ext.lower() not in ('xml','zip'):
                raise ValidationError('Por favor, escoja un archivo ZIP o XML')
            if file_ext.lower() == 'xml':
                raw_file = self.get_raw_file()
                bills = self.get_xml_data(raw_file)
                root = bills[0]['xml']['cfdi:Comprobante']
                vendor = root['cfdi:Receptor']
                vendor2 = root['cfdi:Emisor']
                rfc_receptor = vendor.get('@Rfc') or vendor.get('@rfc')
                rfc_emisor = vendor2.get('@Rfc') or vendor2.get('@rfc')
                #tipo_factura = self.validate_invoice_type(rfc_emisor, rfc_receptor)
                #raise ValidationError(tipo_factura)
                self.validate_invoice_type(rfc_emisor, rfc_receptor)
            else:
                self.invoice_type = False
        else:
            self.invoice_type = False
    
    def validate_invoice_type(self, rfc_emisor, rfc_receptor):
        emisor_company_id = self.env['res.company'].search([('vat','=',rfc_emisor)])
        flag = True
        invoice_type = ''
        if self.company_id == emisor_company_id:
            invoice_type = 'out_invoice'
            self.invoice_type = 'out_invoice'
            flag = False
            #return 'cliente'
        receptor_company_id = self.env['res.company'].search([('vat','=',rfc_receptor)])
        if self.company_id == receptor_company_id:
            invoice_type = 'in_invoice'
            self.invoice_type = 'in_invoice'
            flag = False
            #return 'proveedor'
        if emisor_company_id == receptor_company_id:
            invoice_type = 'invalid_invoice'
            return invoice_type
        if flag:
            invoice_type = 'invalid_invoice'
            return invoice_type
        else:
            return invoice_type

        
    def get_xml_data(self, file):
        '''
            Ordena datos de archivo xml
        '''
        xmls = []
        # convertir byte string a dict
        xml_string = file.decode('utf-8')
        xml_string = self.clean_xml(xml_string)
        xml = xmltodict.parse(xml_string)
        

        xml_file_data = base64.encodestring(file)
        
        #raise ValidationError(self.filename)

        bill = {
            'filename': self.filename,
            'xml': xml,
            'xml_file_data':xml_file_data,
        }
        xmls.append(bill)
            
        return xmls

    def get_xml_from_zip(self, zip_file):
        '''
            Extraer archivos del .zip.
            Convertir XMLs a diccionario para 
            un manejo mas fácil de los datos.
        '''
        xmls = []
        for fileinfo in zip_file.infolist():
            #print(fileinfo.filename)
            file_ext = self.get_file_ext(fileinfo.filename)
            if file_ext in ('xml','XML'):
                #print('entro')
                # convertir byte string a dict
                xml_string = zip_file.read(fileinfo).decode('utf-8')
                xml_string = self.clean_xml(xml_string)
                xml = xmltodict.parse(xml_string)


                xml_file_data = base64.encodestring(zip_file.read(fileinfo))
                bill = {
                    'filename': fileinfo.filename,
                    'xml': xml,
                    'xml_file_data':xml_file_data,
                }
                xmls.append(bill)
            
        return xmls
    
    def clean_xml(self, xml_string):
        # Este método sirve para remover los caracteres que, en algunos XML, vienen al inicio del string antes del primer 
        # caracter '<'
        new_ml_string = xml_string.split('<')
        to_remove = new_ml_string[0]
        #raise ValidationError(to_remove)
        new_ml_string = xml_string.replace(to_remove, '')
        #new_ml_string = new_ml_string.replace('&#xA;',' ')
        #new_ml_string = new_ml_string.replace('&quot;','"')
        
        return new_ml_string

    @api.multi
    def validate_bills(self):
        '''
            Función principal. Controla todo el flujo de 
            importación al clickear el botón (parsea el archivo
            subido, lo valida, obtener datos de la factura y
            guardarla crea factura en estado de borrador).
        ''' 
        #raise ValidationError('qweweqrwe')
        # parsear archivo subido (bye string => .zip)
        #file_ext = self.filename.split('.')[1]
        
        file_ext = self.get_file_ext(self.filename)
        if file_ext.lower() not in ('xml','zip'):
            raise ValidationError('Por favor, escoja un archivo ZIP o XML')

        raw_file = self.get_raw_file()
        zip_file = self.get_zip_file(raw_file)

        if zip_file:
            
            # extraer archivos dentro del .zip
            bills = self.get_xml_from_zip(zip_file)
        else:
            bills = self.get_xml_data(raw_file)

        valid_bills = []
        invalid_bills = []
        for bill in bills:
            mensaje = self.validations(bill)
            if mensaje:
                invalid_bills.append(mensaje)
                continue
                
            invoice, invoice_line, version, invoice_type, bank_id = self.prepare_invoice_data(bill)
            #raise ValidationError(str('after prepare_invoice_data'))
             
            #if invoice_type != 'invalid_invoice':
            bill['bank_id'] = bank_id
            bill['invoice_type'] = invoice_type
            bill['invoice_data'] = invoice
            bill['invoice_line_data'] = invoice_line
            bill['version'] = version
            bill['valid'] = True
            
            mensaje = self.validations(bill)
            if mensaje:
                invalid_bills.append(mensaje)
                continue
            
            valid_bills.append(bill)
            
            #valida que el tipo de comprobante no sea P
            #if invoice['tipo_comprobante'] != 'P':
            #    bill['valid'] = True
            #else:
            #    bill['valid'] = False
            #    bill['state'] = 'Tipo de comprobante no valido: "P"'

        #filtered_bills = self.get_vat_validation(valid_bills)
        # validar ante el SAT
        #if self.sat_validation:
        #    filtered_bills = self.get_sat_validation(valid_bills)
            # mostrar error si un XML no es válido y detener todo
        #self.show_validation_results_to_user(filtered_bills)

        # si todos son válidos, extraer datos del XML
        # y crear factura como borrador
        invoice_ids = []
        invoices_no_created = []
        warning_bills = []
        mensaje3 = ''
        for bill in valid_bills:
            #print('bill: ',bill)
            invoice = bill['invoice_data']
            invoice_line = bill['invoice_line_data']
            invoice_type = bill['invoice_type']
            version = bill['version']
            
            draft, mensaje = self.create_bill_draft(invoice, invoice_line, invoice_type)
            #raise ValidationError(str('after create_bill_draft'))
            #texto = ', '.join(draft)
            draft.compute_taxes()
            #raise ValidationError(draft.tax_line_ids[0].amount)
            #draft.tax_line_ids[0].amount = invoice['amount_tax']
            #raise ValidationError(draft.tax_line_ids[0].amount)
            #se asigna diario
            draft.journal_id = invoice['journal_id']
            draft.account_id = invoice['account_id']
            #raise ValidationError(draft.account_id.name)
            
            #se adjunta xml
            self.attach_to_invoice(draft, bill['xml_file_data'],bill['filename'])
            draft.l10n_mx_edi_cfdi_name = bill['filename']
            
            if invoice_type == 'out_invoice' or invoice_type == 'out_refund':
                draft.l10n_mx_edi_payment_method_id = self.payment_method_customer
                draft.l10n_mx_edi_usage = self.usage_customer
                
                #draft.payment_term_id = draft.partner_id.property_payment_term_id
                # si no se definio termino de pago
                # sumarle 1 dia a la fecha de vencimiento
                #if not draft.payment_term_id and self.payment_term_customer_id:
                #    draft.payment_term_id = self.payment_term_customer_id
                #else:
                    #date_due = datetime.strptime(draft.date_invoice, "%Y-%m-%d")
                #    date_due = draft.date_invoice
                #    date_due = date_due + timedelta(days=1)
                    #print('date_due: ',date_due)
                #    draft.date_due = date_due
                ### Abierta factura cliente
                if self.invoice_status_customer == 'abierta':
                    #se valida factura
                    #draft.action_invoice_open()
                    #if draft.type == 'out_invoice':
                    draft.payment_term_id = self.payment_term_customer_id
                    draft.action_invoice_open()
                    #raise ValidationError('after action_invoice_open')
                    draft.l10n_mx_edi_pac_status = 'signed'
                    draft.l10n_mx_edi_sat_status = 'valid'
                ### Paga factura cliente
                if self.invoice_status_customer == 'pagada':

                    #if draft.type == 'out_invoice':
                    
                    
                    if draft.partner_id.property_payment_term_id:
                        draft.payment_term_id = draft.partner_id.property_payment_term_id
                    else:
                        if self.invoice_payment_type_customer == 'fecha_fin_mes':
                            year = datetime.now().year
                            month = datetime.now().month
                            day = calendar.monthrange(year, month)[1]
                            draft.date_invoice = datetime(year, month, day).date()
                        if self.invoice_payment_type_customer == 'fecha_especifica':
                            if not draft.date_invoice < self.invoice_date_customer:
                                draft.date_invoice = self.invoice_date_customer
                    
                    draft.action_invoice_open()
                    draft.l10n_mx_edi_pac_status = 'signed'
                    draft.l10n_mx_edi_sat_status = 'valid'
                    #si el termino de pago es contado, se valida la factura y se paga
                    # (solo para facturas de venta)
                        
                    if self.is_immediate_term(draft.payment_term_id):
                        # Pago inmediato
                        draft.payment_term_id = 13
                    # print('----------------------->', invoice['metodo_pago'])
                    # if invoice['metodo_pago'] == 'PUE': #pago en una sola exibicion
                        #raise ValidationError('ok')
                        #SE CREA PAGO DE FACTURA
                        #raise ValidationError(bank_id)
                        #raise ValidationError(invoice_type)
                        payment = self.create_payment(draft, bill['bank_id'])
                        #raise ValidationError(payment.account_id)
                        payment.post()
                        #raise ValidationError(draft.l10n_mx_edi_cfdi_name)
            else:
                #draft.payment_term_id = draft.partner_id.property_supplier_payment_term_id
                #if not draft.payment_term_id and self.payment_term_provider_id:
                #    draft.payment_term_id = self.payment_term_provider_id
                ### Abierta factura proveedor
                if self.invoice_status_provider == 'abierta':
                    #se valida factura
                    #draft.action_invoice_open()
                    #if draft.type == 'out_invoice':
                    draft.payment_term_id = self.payment_term_provider_id
                    draft.action_invoice_open()
                    draft.l10n_mx_edi_pac_status = 'signed'
                    draft.l10n_mx_edi_sat_status = 'valid'
                ### Paga factura proveedor
                if self.invoice_status_provider == 'pagada':
                    #raise ValidationError('payment')
                    if draft.partner_id.property_payment_term_id:
                        draft.payment_term_id = draft.partner_id.property_payment_term_id
                    else:
                        if self.invoice_payment_type_provider == 'fecha_fin_mes':
                            year = datetime.now().year
                            month = datetime.now().month
                            day = calendar.monthrange(year, month)[1]
                            draft.date_invoice = datetime(year, month, day).date()
                        if self.invoice_payment_type_provider == 'fecha_especifica':
                            if not draft.date_invoice < self.invoice_date_provider:
                                draft.date_invoice = self.invoice_date_provider
                    
                    draft.action_invoice_open()
                    draft.l10n_mx_edi_pac_status = 'signed'
                    draft.l10n_mx_edi_sat_status = 'valid'
                    
                    if self.is_immediate_term(draft.payment_term_id):
                        # Pago inmediato
                        draft.payment_term_id = 13
                        payment = self.create_payment(draft, bill['bank_id'])
                        #raise ValidationError('payment')
                        payment.post()
            partner_exists = self.get_partner_or_create_validation(draft.partner_id)  
            
            if partner_exists:
                mensaje3 = 'Algunas facturas tienen un contacto con RFC que ya esxite en el sistema, vaya al menu "Contactos por combinar" para poder combinarlos.'
            
            invoice_ids.append(draft.id)

        mensaje1 = 'Facturas cargadas: ' + str(len(invoice_ids)) + '\n'
        mensaje1 = mensaje1 + mensaje3
        mensaje2 = mensaje1 + '\nFacturas no cargadas: ' + str(len(invalid_bills))
        invalids = '\n'.join(invalid_bills)
        mensaje2 = mensaje2 + '\n' + invalids
        view = self.env.ref('xml_to_invoice_extended.sh_message_wizard')
        view_id = view and view.id or False
        context = dict(self._context or {})
        context['message'] = mensaje2
        context['invoice_ids'] = invoice_ids
            
        return {
                'name': 'Advertencia',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'sh.message.wizard',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'context': context
            }

    
    def validations(self, bill):
        #raise ValidationError('asdsa')
        root = bill['xml']['cfdi:Comprobante']
        ######## Tipo comprobante
        tipo_comprobante = root.get('@TipoDeComprobante') or root.get('@tipoDeComprobante')
        if tipo_comprobante.upper() in ['P','N']:
            mensaje = '{} - El XML contiene un Tipo de Comprobante {} que por el momento no puede ser procesado.'.format(bill['filename'], tipo_comprobante)
            return mensaje
        ######## Valida compañía
        vendor = root['cfdi:Receptor']
        vendor2 = root['cfdi:Emisor']
        rfc_receptor = vendor.get('@Rfc') or vendor.get('@rfc')
        rfc_emisor = vendor2.get('@Rfc') or vendor2.get('@rfc')
        #raise ValidationError(rfc_receptor + ' ' +bill['filename'])
        invoice_type = self.validate_invoice_type(rfc_emisor, rfc_receptor)
        
        if invoice_type == 'invalid_invoice':
            mensaje = '{} - La factura no corresponde a la compañía actual.'.format(bill['filename'])
            return mensaje
        ######## Valida Serie
        serie = root.get('@Serie') or root.get('@serie')
        #if not serie:
        #    mensaje = '{} - El xml no contiene el atributo serie'.format(bill['filename'])
        #    return mensaje
        warehouse_id = False
        if invoice_type == 'out_invoice':
            serie_found = False
            if len(self.company_id.xml_import_line_ids) == 0:
                mensaje = '{} - La compañia actual no tiene configurado un diario para la serie del xml.'.format(bill['filename'])
                return mensaje
        
            #for line in self.company_id.xml_import_line_ids:
            #    if line.xml_import_journal_id.sequence_id.name == serie:
            #        warehouse_id = line.xml_import_warehouse_id.id
            #        serie_found = True
            #        break
            #if not serie_found:
            #    mensaje = '{} - No se encontro un diario configurado con la serie {} en la compañia seleccionada. Por favor configure uno.'.format(bill['filename'], serie)
            #    return mensaje
        ####### Valida almacén en facturas de provedor
        if invoice_type == 'in_invoice':
            warehouse_id = self.warehouse_provider_id and self.warehouse_provider_id.id or False
            if not warehouse_id:
                mensaje = '{} - Es una factura de proveedor y no se seleccionó un almacén.'.format(bill['filename'])
                return mensaje
        ####### Valida factura duplicada
        amount_total = root.get('@Total') or root.get('@total')
        date_invoice = root.get('@Fecha') or root.get('@fecha')
        no_certificado = root.get('@NoCertificado') or root.get('@nocertificado')
        folio = root.get('@Folio') or root.get('@folio')
        invoice_name = folio
        if serie and folio:
            invoice_name = serie + ' ' + folio
        else:
            invoice_name = no_certificado
        #else:
        #    mensaje = '{} - No existe serie ({}) o folio ({}) en el xml.'.format(bill['filename'], serie, folio)
        #    return mensaje
        if self.valdiate_duplicate_invoice(rfc_receptor,amount_total,date_invoice,invoice_name):
            mensaje = '{} - Esta factura ya existe en el sistema.'.format(bill['filename'])
            return mensaje
        ####### Valida código SAT de producto
        if 'invoice_line_data' in bill:
            invoice_line = bill['invoice_line_data']
            for product in invoice_line:
                uom = False
                if self.import_type != 'start_amount':
                    uom = self.get_uom(product.get('sat_uom'))
                    if uom:
                        uom = uom[0].id
                    else:
                        uom = False

                        mensaje = '{} - La clave de undiad {} del XML no está asociada a ninguna unidad de medida del sistema.'.format(bill['filename'], product.get('sat_uom'))
                        return mensaje
        ###### Valida productos
        #products_new = self.get_product_or_create_validation(root['cfdi:Conceptos']['cfdi:Concepto'])
        #if not products_new:
        #    mensaje = '{} - Algunos productos en la factura no existen en el sistema, se crearán productos temporales en el menu "Productos por aprobar" que tendrá que validar para poder procesar esta factura.'.format(bill['filename'])
        #    return mensaje
            
        return False
    
    def get_partner_or_create_validation(self, partner):

        search_domain = [
            #'|', # obtener por nombre o RFC
            #('name', '=', partner['name']), 
            ('vat', '=', partner.vat),
            ('active', '=', True),
        ]

        if self.invoice_type == 'out_invoice' or self.invoice_type == 'out_refund':
            search_domain.append(('customer','=',True))
        else:
            search_domain.append(('supplier','=',True))

        p = self.env['res.partner'].search(search_domain)
        #raise ValidationError(str(p))
        if len(p) > 1:
            #rfc_exists = self.env['partner.mix'].search([('rfc','=',partner.vat)])
            #if len(rfc_exists) == 0:
            #    new_rfcs = []
            #    new_rfcs.append({'rfc': partner.vat})
            #    rfcs = self.env['partner.mix'].create(new_rfcs)
            return True

        return False
    
    def get_partner_or_create(self, partner):
        """
        sobrescritura de metodo, los nuevos partner se crearan con
        termino de pago 0 (contado), a menos que se especifique uno distinto
        """
        '''Obtener ID de un partner (proveedor). Si no existe, lo crea.'''
        search_domain = [
            #'|', # obtener por nombre o RFC
            ('name', '=', partner['name']), 
            ('vat', '=', partner['rfc']),
            ('active', '=', True),
        ]

        if self.invoice_type == 'out_invoice' or self.invoice_type == 'out_refund':
            search_domain.append(('customer','=',True))
        else:
            search_domain.append(('supplier','=',True))

        p = self.env['res.partner'].search(search_domain)

        #revisar si es rfc generico
        #indica si se creara un partner generico
        create_generic = False

        if partner['rfc'] in ('XEXX010101000', 'XAXX010101000'):
            for partner_rec in p:
                if partner_rec.name == partner['name']:
                    p = [partner_rec,]
                    break
            else:
                #si no encuentra un match de nombre, crear generico
                create_generic = True


        if not p or create_generic:
            # crear si el proveedor no existe
            payment_term_id = False
            if self.payment_term_id:
                payment_term_id = self.payment_term_id
            else:
                # se obtiene el termino de pago de inmediato
                payment_term_line_id = self.get_payment_term_line(0)
                if payment_term_line_id:
                    payment_term_id = payment_term_line_id.payment_id

            fiscal_position_code = partner.get('position_id')
            fiscal_position = self.env['account.fiscal.position'].search(
                [('l10n_mx_edi_code','=',fiscal_position_code)])
            fiscal_position = fiscal_position and fiscal_position[0]
            fiscal_position_id = fiscal_position.id or False

            vals = {
                'name': partner['name'],
                'vat': partner['rfc'],
                'property_account_position_id': fiscal_position_id,
            }

            if self.invoice_type == 'out_invoice' or self.invoice_type == 'out_refund':
                vals['property_payment_term_id'] = payment_term_id and payment_term_id.id or False
                vals['customer'] = True
                vals['supplier'] = False
            else:
                vals['property_supplier_payment_term_id'] = payment_term_id and payment_term_id.id or False
                vals['customer'] = False
                vals['supplier'] = True

            p = self.env['res.partner'].create(vals)
        else:
            p = p[0]

        return p
    
    def get_product_or_create_validation(self, products):
        """
        sobrescritura de metodo,
        buscara el nombre del xml en el campo 'custom_name'
        de producto,
        se utilizara un ilike en el dominio
        luego se separara el valor del campo por el limitador '|'
        y se buscara que el nombre sea exacto
        """
        #raise ValidationError('ok')
        if not isinstance(products, list):
            products = [products]
        
        products_ok = []
        products_new = []
        
        for product in products:
            invoice_line = {}

            extra_line = {} 
            
            invoice_line['name'] = product.get('@Descripcion') or product.get('@descripcion')
            cantidad = float(product.get('@Cantidad') or product.get('@cantidad'))
            importe = float(product.get('@Importe') or product.get('@importe'))
            valor_unitario = str(importe/cantidad)
            invoice_line['price_unit'] = valor_unitario
            #datos para creacion de producto
            invoice_line['sat_product_ref'] = product.get('@ClaveProdServ') or product.get('@claveProdServ')
            invoice_line['product_ref'] = product.get('@NoIdentificacion') or product.get('@noIdentificacion')
            invoice_line['sat_uom'] = product.get('@ClaveUnidad') or product.get('@claveUnidad')


            p = self.env['product.product'].search([
                ('name', '=', invoice_line['name'])
            ])
            p = p[0] if p else False

            if p:
                continue

            #si no se encontro por nombre, se busca por custom_name
            p = self.env['product.product'].search([
                ('custom_name', 'ilike', invoice_line['name']),
                ('active', '=', True),
            ])
            
            flag = False
            for rec in p:
                for name in p.custom_name.split('|'):
                    if invoice_line['name'].lower() == name.strip().lower():
                        #products_ok.append(rec)
                        flag = True
            if flag:
                continue

            # crear producto si no existe
            if self.create_product:

                EdiCode = self.env["l10n_mx_edi.product.sat.code"]

                product_vals = {
                    'name': invoice_line['name'],
                    'price': invoice_line['price_unit'],
                    'default_code': invoice_line['product_ref'],
                    'type': 'product',
                }

                sat_code = EdiCode.search([("code","=",invoice_line['sat_product_ref'])])
                # #print("sat_code = ",sat_code)
                if sat_code:
                    product_vals["l10n_mx_edi_code_sat_id"] = sat_code[0].id

                uom = self.get_uom(invoice_line['sat_uom'])
                if uom:
                    product_vals["uom_id"] = uom[0].id
                    product_vals["uom_po_id"] = uom[0].id
                #raise ValidationError(str(product_vals))
                temporal_product = self.env['approval.product'].search([('name','=',product_vals['name'])])
                #raise ValidationError(str(temporal_product))
                if len(temporal_product) > 0:
                    continue
                
                p = self.env['approval.product'].create(product_vals)
                
                #raise ValidationError(str(p))
                products_new.append(p)
        
        if len(products_new) > 0:
            return False
        else:
            return True
        
    def get_product_or_create(self, product):
        """
        sobrescritura de metodo,
        buscara el nombre del xml en el campo 'custom_name'
        de producto,
        se utilizara un ilike en el dominio
        luego se separara el valor del campo por el limitador '|'
        y se buscara que el nombre sea exacto
        """
        #print('get_product_or_create')
        #primero se busca por nombre
        p = self.env['product.product'].search([
            ('name', '=', product['name'])
        ])
        p = p[0] if p else False
        
        if p:
            return p.id

        #si no se encontro por nombre, se busca por custom_name
        p = self.env['product.product'].search([
            ('custom_name', 'ilike', product['name']),
            ('active', '=', True),
        ])
        
        for rec in p:
            for name in rec.custom_name.split('|'):
                if product['name'].lower() == name.strip().lower():
                    return rec.id
        # # si no se encontro ninguno incluir datos de producto en 
        # # mensaje de error
        # self.products_valid = False
        # self.products_error_msg += str(product['name']) + "\n"
        # return False
        
        # crear producto si no existe
        if self.create_product:
            
            EdiCode = self.env["l10n_mx_edi.product.sat.code"]

            product_vals = {
                'name': product['name'],
                'custom_name': product['name'],
                'price': product['price_unit'],
                'default_code': product['product_ref'],
                'type': 'product',
            }

            sat_code = EdiCode.search([("code","=",product['sat_product_ref'])])
            # #print("sat_code = ",sat_code)
            if sat_code:
                product_vals["l10n_mx_edi_code_sat_id"] = sat_code[0].id

            uom = self.get_uom(product['sat_uom'])
            # #print(product['sat_uom'])
            # #print("uom = ",uom)
            if uom:
                product_vals["uom_id"] = uom[0].id
                product_vals["uom_po_id"] = uom[0].id

            
            p = self.env['product.product'].create(product_vals)
            
        return p.id
    
    def valdiate_duplicate_invoice(self,vat,amount_total,date,invoice_name):
        """
        REVISA SI YA EXISTE LA FACTURA EN SISTEMA
        DEVUELVE TRUE SI YA EXISTE
        FALSE SI NO
        """

        date = date.split('T')[0]
        AccountInvoice = self.env['account.invoice'].sudo()
        #raise ValidationError(str(vat) +' - '+str(round(float(amount_total),2)) + ' - '+str(date))
        domain = [
            ('partner_id.vat','=',vat),
            ('amount_total','=',round(float(amount_total),2)),
            ('date_invoice','=',date),
            ('state','!=','cancel'),
        ]
        if self.invoice_type == 'out_invoice' or self.invoice_type == 'out_refund':
            #FACTURA CLIENTE
            domain.append(('name','=',invoice_name))
        else:
            #FACTURA PROVEEDOR
            domain.append(('reference','=',invoice_name))
        invoices = AccountInvoice.search(domain)
        #domain = [
        #    ('name','=',invoice_name),
        #    ('state','!=','cancel')
        #]
        #invoices2 = AccountInvoice.search(domain)
        #print('domain: ',domain)
        #print('invoices: ',invoices)

        #print('test_invoice.date: ',test_invoice.date)
        if invoices:
            print('DUPLICADA: ',invoices)
            return True
        return False

    
    def create_payment(self, invoice, bank_id):
        
        """
        Crea pago para la factura indicada
        """
        AccountRegisterPayments = self.env['account.register.payments'].sudo()
        if invoice.type == 'out_invoice':
            payment_type = 'inbound' if invoice.type in ('out_invoice', 'in_refund') else 'outbound'
            if payment_type == 'inbound':
                payment_method = self.env.ref('account.account_payment_method_manual_in')
                #journal_payment_methods = pay_journal.inbound_payment_method_ids
            else:
                payment_method = self.env.ref('account.account_payment_method_manual_out')
                #journal_payment_methods = pay_journal.outbound_payment_method_ids
            #print('self.payment_journal_id.id: ',self.payment_journal_id.id)
           
            vals = {
                'amount': invoice.amount_total or 0.0,
                'currency_id': invoice.currency_id.id,
                'journal_id': bank_id,
                'payment_type': payment_type,
                'payment_method_id': payment_method.id,
                'group_invoices': False,
                'invoice_ids': [(6, 0, [invoice.id])],
                'multi': False,
                'payment_date': invoice.date_invoice,
            }
        if invoice.type == 'in_invoice':
            #raise ValidationError(payment_type)
            vals = {
                'amount': invoice.amount_total or 0.0,
                'currency_id': invoice.currency_id.id,
                'journal_id': bank_id,
                'payment_type': False,
                'payment_method_id': False,
                'group_invoices': False,
                'invoice_ids': [(6, 0, [invoice.id])],
                'multi': False,
                'payment_date': invoice.date_invoice,
            }
        account_register_payment_id = AccountRegisterPayments.with_context({'active_ids': [invoice.id,]}).create(vals)
        payment_vals = account_register_payment_id.get_payments_vals()

        AccountPayment = self.env['account.payment'].sudo()
        return AccountPayment.create(payment_vals)

    
    def add_products_to_invoice(self, products, default_account, account_analytic_id, invoice_type):
        '''
            Obtener datos de los productos (Conceptos).
            SE SOBRESCRIBE PARA AGREGAR INFO DE CUENTA ANALITICA
        '''
        all_products = []

        # asegurarse de que `products` es una lista
        # para poder iterar sobre ella
        if not isinstance(products, list):
            products = [products]

        exent_tax = self.get_extra_line_tax()
        exent_tax = exent_tax and exent_tax.id or False
        extra_line_account_id = self.get_extra_line_account()

        # crear un dict para cada producto en los conceptos
        for product in products:
            # datos básicos
            invoice_line = {}

            extra_line = {} #se usara para productos gasolina, contendra lineas extra
            
            invoice_line['name'] = product.get('@Descripcion') or product.get('@descripcion')
            invoice_line['quantity'] = product.get('@Cantidad') or product.get('@cantidad')
            invoice_line['price_subtotal'] = product.get('@Importe') or product.get('@importe')
            # A. Marquez 28/12/19: Para obtener el valor unitario "correcto"
            cantidad = float(invoice_line['quantity'])
            importe = float(invoice_line['price_subtotal'])
            valor_unitario = str(importe/cantidad)
            ###
            #invoice_line['price_unit'] = product.get('@ValorUnitario') or product.get('@valorUnitario')
            invoice_line['price_unit'] = valor_unitario
            #datos para creacion de producto
            invoice_line['sat_product_ref'] = product.get('@ClaveProdServ') or product.get('@claveProdServ')
            invoice_line['product_ref'] = product.get('@NoIdentificacion') or product.get('@noIdentificacion')
            invoice_line['sat_uom'] = product.get('@ClaveUnidad') or product.get('@claveUnidad')

            analytic_tag_ids = False
            if invoice_type == 'out_invoice':
                if self.line_analytic_tag_customer_ids:
                    analytic_tag_ids = [(6, None, self.line_analytic_tag_customer_ids.ids)]
            else:
                if self.line_analytic_tag_provider_ids:
                    analytic_tag_ids = [(6, None, self.line_analytic_tag_provider_ids.ids)]

            invoice_line['analytic_tag_ids'] = analytic_tag_ids
            invoice_line['account_analytic_id'] = account_analytic_id
            if invoice_type == 'out_invoice':
                invoice_line['account_id'] = default_account or self.cuenta_ingreso_cliente_id.id
            else:
                invoice_line['account_id'] = default_account or self.cuenta_gasto_proveedor_id.id

            # calcular porcentaje del descuento, si es que hay 
            if product.get('@Descuento'):
                invoice_line['discount'] = self.get_discount_percentage(product)
            else:
                invoice_line['discount'] = 0.0

            # obtener id del producto
            # crear producto si este no existe
            invoice_line['product_id'] = self.get_product_or_create(invoice_line)
            
            #raise ValidationError(str('after get_product_or_create'))
            # si el producto tiene impuestos, obtener datos
            # y asignarselos al concepto
            tax_group = ''
            check_taxes = product.get('cfdi:Impuestos')
            if check_taxes:
                invoice_taxes = []
                if check_taxes.get('cfdi:Traslados'):
                    traslado = {}
                    t = check_taxes['cfdi:Traslados']['cfdi:Traslado']
                    #print('---t----: ',t)
                    if not isinstance(t,list):
                        t = [t,]
                    for element in t:
                        # revisa rsi es gasolina el producto
                        tax_base = element.get('@Base')
                        # si la base del impuesto no coincide con el subtotal del producto
                        # es que es gasolina
                        if tax_base != invoice_line['price_subtotal']:
                            #print("es gasolina")
                            new_price = float(tax_base) / float(invoice_line['quantity'])
                            invoice_line['price_unit'] = new_price

                            #calcular precio de linea extra
                            extra_line_price = float(invoice_line['price_subtotal']) - float(tax_base)

                            #revisar si no es necesario recalcular el subtotal
                            # invoice_line['price_unit'] = new_price * invoice_line['quantity']

                            extra_account_id = extra_line_account_id and extra_line_account_id.id or False
                            if not extra_account_id:
                                raise ValidationError('No se encontro una cuenta de combustible configurada')

                            #crear linea extra
                            extra_line = {
                                'name': invoice_line['name'],
                                'quantity': 1,
                                #'product_id': invoice_line['product_id'],
                                'price_unit': extra_line_price,
                                'price_subtotal': extra_line_price,
                                'sat_product_ref': invoice_line['sat_product_ref'],
                                'product_ref': invoice_line['product_ref'],
                                'sat_uom': invoice_line['sat_uom'],
                                'ignore_line': True,
                                'account_id': extra_line_account_id and extra_line_account_id.id or False,
                                'account_analytic_id': account_analytic_id,
                                'analytic_tag_ids': False,
                            }

                            if exent_tax:
                                extra_line['taxes'] = [(6, None, (exent_tax,))]

                        tax_code = element.get('@Impuesto','')
                        tax_rate = element.get('@TasaOCuota','0')
                        tax_factor = element.get('@TipoFactor','')
                        tax_group =  tax_group + tax_code + '|' + tax_rate + '|tras|' + tax_factor + ','
                        #raise ValidationError(tax_group)
                        #print('tax_group: ',tax_group)
                        #tax = self.get_tax_ids(tax_group)
                        #print('tax: ',tax)
                        #traslado['tax_id'] = tax
                        #invoice_taxes.append(tax)

                if check_taxes.get('cfdi:Retenciones'):
                    retencion = {}
                    r = check_taxes['cfdi:Retenciones']['cfdi:Retencion']
                    #print('---r----: ',r)
                    if not isinstance(r,list):
                        r = [r,]
                    for element in r:
                        #retencion['amount'] = element.get('@Importe') or element.get('@importe')
                        #retencion['base'] = element.get('@Base')
                        #retencion['account_id'] = 23
                        tax_code = element.get('@Impuesto','')
                        tax_rate = element.get('@TasaOCuota','0')
                        tax_factor = element.get('@TipoFactor','')
                        tax_group =  tax_group + tax_code + '|' + tax_rate + '|ret|' + tax_factor + ','
                        #print('tax_group: ',tax_group)
                        #tax = self.get_tax_ids(tax_group)
                        #print('tax: ',tax)
                        #retencion['tax_id'] = tax
                        #invoice_taxes.append(tax)
                taxes = False
                if tax_group:
                    taxes = self.get_tax_ids(tax_group)
                #print('taxes: ',taxes)
                invoice_line['taxes'] = taxes

            # agregar concepto a la lista de conceptos
            all_products.append(invoice_line)

            #se agrega linea extra, de existir
            if extra_line:
                all_products.append(extra_line)
        
        return all_products
    
    
    def create_bill_draft(self, invoice, invoice_line, invoice_type):
        '''
            Toma la factura y sus conceptos y los guarda
            en Odoo como borrador.
        '''
        
        #print("invoice['type']: ",invoice['type'])
        vals = {
            #'name': name,
            'l10n_mx_edi_cfdi_name': invoice['l10n_mx_edi_cfdi_name'],
            'l10n_mx_edi_cfdi_name2': invoice['l10n_mx_edi_cfdi_name'],
            'journal_id': invoice['journal_id'],
            'team_id': invoice['team_id'],
            'user_id': invoice['user_id'],
            'account_id': invoice['account_id'],

            'date_invoice': invoice['date_invoice'],
            'account_id': invoice['account_id'],
            'partner_id': invoice['partner_id'],
            'amount_untaxed': invoice['amount_untaxed'],
            #'amount_tax': invoice['amount_tax'],
            'amount_total': invoice['amount_total'],
            'currency_id': invoice['currency_id'],
            'type': invoice['type'],
            'warehouse_id': invoice['warehouse_id'],
            'is_start_amount': True if self.import_type == 'start_amount' else False,
        }

        if invoice_type == 'out_invoice' or invoice_type == 'out_refund':
            vals['name'] = invoice['name']
        else:
            vals['reference'] = invoice['name']
            vals['create_return'] = False
        
        # How to create and validate Vendor Bills in code? 
        # https://www.odoo.com/forum/ayuda-1/question/131324
        draft = self.env['account.invoice'].create(vals)
        # asignar productos e impuestos a factura
        for product in invoice_line:
            #if product['price_subtotal'] == '3.02':
            #    raise ValidationError(product['price_subtotal'], 'ok')
            uom = False
            if self.import_type != 'start_amount':
                uom = self.get_uom(product.get('sat_uom'))
                if uom:
                    uom = uom[0].id
                else:
                    uom = False
                    
                    mensaje = '{} - La unidad de medida ' + str(product.get('sat_uom')) + ' del XML no existe en el sistema.'
                    return False, mensaje
            #raise ValidationError(str(product.get('product_id')))
            self.env['account.invoice.line'].create({
                'product_id': product.get('product_id'),
                'invoice_id': draft.id,
                'name': product['name'],
                'quantity': product['quantity'],
                'price_unit': product['price_unit'],
                'account_id': product['account_id'],
                'discount': product.get('discount') or 0.0,
                'price_subtotal': product['price_subtotal'],
                'invoice_line_tax_ids': product.get('taxes'),
                'uom_id': uom,
                'analytic_tag_ids': product['analytic_tag_ids'],
                'account_analytic_id': product['account_analytic_id'],
            })

        return draft, False
    
    
    def prepare_invoice_data(self, bill):
        '''
            Obtener datos del XML y wizard para llenar factura
            Returns:
                invoice: datos generales de la factura.
                invoice_line: conceptos de la factura.
        '''
        
        # aquí se guardaran los datos para su posterior uso
        invoice = {}
        invoice_line = []
        partner = {}

        filename = bill['filename']

        # elementos principales del XML
        root = bill['xml']['cfdi:Comprobante']

        # revisa version
        version = root.get('@Version') or root.get('@version') or ''
        #print('root: ',root)
        #print('version: ',version)
        vendor = root['cfdi:Receptor']
        vendor2 = root['cfdi:Emisor']
        rfc_receptor = vendor.get('@Rfc') or vendor.get('@rfc')
        rfc_emisor = vendor2.get('@Rfc') or vendor2.get('@rfc')
        
        invoice_type = self.validate_invoice_type(rfc_emisor, rfc_receptor)

        if invoice_type == 'out_invoice' or invoice_type == 'out_refund':
            # xml de cliente
            vendor = root['cfdi:Receptor']
            vendor2 = root['cfdi:Emisor']
        else:
            # xml de proveedor
            vendor = root['cfdi:Emisor']
            vendor2 = root['cfdi:Receptor']
            
        #obtener datos del partner
        partner['rfc'] = vendor.get('@Rfc') or vendor.get('@rfc')
        invoice['rfc'] = vendor.get('@Rfc') or vendor.get('@rfc')
        invoice['company_rfc'] = vendor2.get('@Rfc') or vendor2.get('@rfc')
        partner['name'] = vendor.get('@Nombre',False) or vendor.get('@nombre','PARTNER GENERICO: REVISAR')
        partner['position_id'] = vendor.get('@RegimenFiscal')
        partner_rec = self.get_partner_or_create(partner)
        default_account = partner_rec.default_xml_import_account and \
                    partner_rec.default_xml_import_account.id or False
        #print('default_account: ',default_account)
        partner_id = partner_rec.id


        serie = root.get('@Serie') or root.get('@serie')
        folio = root.get('@Folio') or root.get('@folio')
        no_certificado = root.get('@NoCertificado') or root.get('@nocertificado')
        metodopago = root.get('@MetodoPago') or root.get('@metodoPago') or False
        forma_pago = root.get('@FormaPago') or root.get('@formaPago')
        uso_cfdi = root['cfdi:Receptor'].get('@UsoCFDI') or root['cfdi:Receptor'].get('@usoCFDI')

        journal_id, analytic_account_id, warehouse_id, bank_id =self.get_company_xml_import_data(invoice_type, serie)
        #raise ValidationError(bank_id)
        invoice['journal_id'] = journal_id
        invoice['warehouse_id'] = warehouse_id
        invoice['metodo_pago'] = metodopago

        forma_pago_rec = self.get_edi_payment_method(forma_pago)
        print('forma_pago_rec: ',forma_pago_rec)
        print('uso_cfdi: ',uso_cfdi)
        invoice['l10n_mx_edi_payment_method_id'] = forma_pago_rec and forma_pago_rec.id or False
        invoice['l10n_mx_edi_usage'] = uso_cfdi

        # obtener datos de los conceptos.
        # invoice_line es una lista de diccionarios
        #invoice_line = self.add_products_to_invoice(root['cfdi:Conceptos']['cfdi:Concepto'])
        #11 nov/14B60424-DED8-4279-BB00-7BDE3BBB4BB7.xml
        if self.import_type == 'start_amount':
            #print('filename: ',filename)
            # carga de saldfos iniciales, las lineas se agrupan por impuesto
            if version == '3.3':
                invoice_line = self.compact_lines(root['cfdi:Conceptos']['cfdi:Concepto'], default_account)
            else:
                #print('111111')
                taxes = self.get_cfdi32_taxes(root['cfdi:Impuestos'])
                invoice_line = self.get_cfdi32(root['cfdi:Conceptos']['cfdi:Concepto'], taxes, default_account, analytic_account_id)
        else:
            # carga de factura regular
            invoice_line = self.add_products_to_invoice(root['cfdi:Conceptos']['cfdi:Concepto'], default_account, analytic_account_id, invoice_type)
        #raise ValidationError(str('after add_products_to_invoice'))
        # obtener datos de proveedor
        # crear al proveedor si no existe
        # #print('VENDOR: ',vendor.get('@Nombre'))
        # #print('VENDOR: ',vendor.get('@nombre'))
        tipo_comprobante = root.get('@TipoDeComprobante') or root.get('@tipoDeComprobante')
        #raise ValidationError(tipo_comprobante)
        invoice['tipo_comprobante'] = tipo_comprobante
        #SE CORRIGE TIPO SEGUN EL TIPO DE COMPROBANTE
        # SOLO TOMA EN CUENTA INGRESOS Y EGRESOS
        #print('tipo_comprobante: ',tipo_comprobante)
        corrected_invoice_type = False
        if tipo_comprobante.upper() == 'E':
            if invoice_type == 'out_invoice':
                #print('out_refund')
                corrected_invoice_type = 'out_refund'
            else:
                #print('in_refund')
                corrected_invoice_type= 'in_refund'



        # partner['rfc'] = vendor.get('@Rfc') or vendor.get('@rfc')
        # invoice['rfc'] = vendor.get('@Rfc') or vendor.get('@rfc')
        # invoice['company_rfc'] = vendor2.get('@Rfc') or vendor2.get('@rfc')
        # partner['name'] = vendor.get('@Nombre',False) or vendor.get('@nombre','PARTNER GENERICO: REVISAR')

        # partner['position_id'] = vendor.get('@RegimenFiscal')
        # partner_id = self.get_partner_or_create(partner)
        moneda = root.get('@Moneda') or root.get('@moneda') or 'MXN'
        #print('moneda.upper(): ',moneda.upper())
        if moneda.upper() in ('M.N.','XXX','PESO MEXICANO'):
            moneda = 'MXN'

        # obtener datos generales de la factura
        currency = self.env['res.currency'].search([('name', '=', moneda)])
        #print('self.invoice_type: ',self.invoice_type)
        #invoice['type'] = 'in_invoice' # factura de proveedor

        invoice['type'] = corrected_invoice_type or invoice_type

        invoice['name'] = folio
        if serie and folio:
            invoice['name'] = serie + ' ' + folio
        else:
            invoice['name'] = no_certificado

        invoice['amount_untaxed'] = root.get('@SubTotal') or root.get('@subTotal')
        invoice['amount_tax'] = ''
        #if 'cfdi:Impuestos' in root:
            #raise ValidationError(str(folio))
        
            #invoice['amount_tax'] = root['cfdi:Impuestos']['cfdi:Traslados']['cfdi:Traslado'].get('@Importe')
        invoice['amount_total'] = root.get('@Total') or root.get('@total')
        invoice['partner_id'] = partner_id
        invoice['currency_id'] = currency.id
        invoice['date_invoice'] = root.get('@Fecha') or root.get('@fecha')
        #invoice['account_id'] = self.env['account.invoice']._default_journal().id

        ####
        invoice['l10n_mx_edi_cfdi_name'] = filename
        #invoice['l10n_mx_edi_cfdi_name2'] = filename #DENOTA QUE SE CARGO POR MEDIO DE ESTE MODULO
        #invoice['journal_id'] = self.journal_id and self.journal_id.id or False
        invoice['team_id'] = self.team_id and self.team_id.id or False
        invoice['user_id'] = self.user_id and self.user_id.id or False
        if invoice_type == 'out_invoice':
            invoice['account_id'] = self.cuenta_cobrar_cliente_id.id
        else:
            invoice['account_id'] = self.cuenta_pagar_proveedor_id.id
        #print('invoice_line: ',invoice_line)
        #OBTENER UUID
        uuid = root['cfdi:Complemento']['tfd:TimbreFiscalDigital'].get('@UUID')
        #print(root['cfdi:Complemento']['tfd:TimbreFiscalDigital'])
        #print('UUID: ',uuid)
        invoice['uuid'] = uuid
        return invoice, invoice_line, version, invoice_type, bank_id

    def get_company_xml_import_data(self, invoice_type, serie=False):
        """
        -para xmls de cliente
        obtiene el diario, almacen, cuenta analitica
        segun la serie
        -para xmls de proveedor:
        obtiene el diario del wizard
        regresa jorunal_id, analytic_account_id, warehouse_id
        """
        #print('get_company_xml_import_data')
        #print('---> SERIE: ',serie)
        journal_id = False
        analytic_account_id = False
        warehouse_id = False
        if invoice_type == 'out_invoice':
            serie_found = False
            
            for line in self.company_id.xml_import_line_ids:
                
                if line.xml_import_journal_id.sequence_id.name == serie:
                    journal_id = line.xml_import_journal_id.id
                    analytic_account_id = line.xml_import_analytic_account_id.id
                    warehouse_id = line.xml_import_warehouse_id.id
                    bank_id = line.xml_import_bank_id.id
                    serie_found = True
                    #if x == 1:
                    #    pass
                    #raise ValidationError(str(line.xml_import_bank_id.id) + ' - ' + str(serie))
                    break
            
            if not serie_found:
                journal_id = self.company_id.xml_import_line_ids[0].xml_import_journal_id.id
                analytic_account_id = self.company_id.xml_import_line_ids[0].xml_import_analytic_account_id.id
                warehouse_id = self.company_id.xml_import_line_ids[0].xml_import_warehouse_id.id
                bank_id = self.company_id.xml_import_line_ids[0].xml_import_bank_id.id
                
            # for journal in self.company_id.xml_import_journal_ids:
            #     if journal.sequence_id.name == serie:
            #         journal_id = journal.id
            #         break
        else:
            #if invoice_type == 'out_invoice':
            #    journal_id = self.journal_customer_id.id
            #    analytic_account_id = self.line_analytic_account_customer_id.id
            #    warehouse_id = self.warehouse_customer_id and self.warehouse_customer_id.id or False
            #else:
            journal_id = self.journal_provider_id.id
            analytic_account_id = self.line_analytic_account_provider_id.id
            warehouse_id = self.warehouse_provider_id and self.warehouse_provider_id.id or False
            bank_id = self.payment_journal_provider_id.id
        return journal_id, analytic_account_id, warehouse_id, bank_id
    
class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    
    @api.multi
    def create_pickings(self):
        """
        se recorren facturas y se verifica si las facturas son notas de credito
        """
        print('create_pickings')
        #****proceso de creacion de pickings si es nota de credito****

        if self.create_return:
            # StockPicking = self.env['stock.picking'].sudo()
            StockPicking = self.env['stock.picking']

            #se recorren facturas y se verifica si las facturas son notas de credito
            for invoice in self:
                print('***',invoice.type)
                #if invoice.type in ('in_refund','out_refund'):

                picking_type = invoice.get_picking_type()
                line_vals = self.get_picking_lines()

                location_id, location_dest_id = self.get_picking_locations(picking_type)
                
                date = datetime.strptime(str(invoice.date_invoice)+ ' 6:00:00', DEFAULT_SERVER_DATETIME_FORMAT)
                picking_vals = {
                    'partner_id': self.partner_id.id,
                    'picking_type_id': picking_type and picking_type.id,
                    'location_id': location_id,
                    'location_dest_id': location_dest_id,
                    'origin': invoice.number,
                    'move_lines': line_vals,
                    'invoice_id': invoice.id,
                    'is_return_picking': True,
                    'scheduled_date': date,
                    'date_done': date
                }
                self.process_picking_errors(picking_vals,picking_type)
                print('se va a crear picking')
                print('line_vals: ',line_vals)
                if line_vals != []:
                    picking = StockPicking.create(picking_vals)
                    print('picking_id: ', picking.id)
                    #validar picking:
                    picking.action_confirm()
                    picking.action_done()
                    print('done')
                    if picking.state != 'done':
                        raise ValidationError('Error al crear devolucion!\nEl movimiento de devolucion no pudo ser completado!')
        return