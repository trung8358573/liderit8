from openerp.osv import osv, fields
from openerp import api
from datetime import datetime
import os, glob, csv
import logging
_logger = logging.getLogger(__name__)


class tercap_import_document(osv.osv):
    _name = 'tercap.import.document'
    _columns = {
            'name' : fields.char(),
            'numdocumento' : fields.char('Num Documento',size=20),
            'fechadocumento' : fields.date('Fecha Documento'),
            'tipodocumento' : fields.float('Tipo Documento',digits=(3,0)),
            'serie' : fields.char('Serie', size=4),
            'docespecial' : fields.char('Documento Especial', size=3),
            'codempresa' : fields.float('Codigo de empresa', digits=(9,0)),
            'codigoruta' : fields.float('Codigo de la ruta', digits=(4,0)),
            'codvendedor' : fields.float('Codigo del vendedor', digits=(9,0)),
            'codcliente' : fields.float('Codigo de cliente en TERCAP', digits=(9,0)),
            'coddireccion' : fields.float('Codigo de direccion en TERCAP', digits=(9,0)),
            'fechaentrega' : fields.date('Fecha de entrega prevista'),
            'codclientealternativo' : fields.char('Codigo de cliente alternativo', size=20),
            'coddirealternativo' : fields.char('Codigo de direccion alternativo', size=20),
            'documentoorigen' : fields.char('Numero del documento de origen', size=20),
            'base1' : fields.float('Base imponible normal', digits=(10,3)),
            'base2' : fields.float('Base imponible reducido', digits=(10,3)),
            'base3' : fields.float('Base imponible super-reducido', digits=(10,3)),
            'descuento' : fields.float('Porcentaje descuento', digits=(10,3)),
            'descuentopp' : fields.float('Porcentaje descuento pronto pago', digits=(10,3)),
            'iva1' : fields.float('Cuota IVA normal', digits=(10,3)),
            'iva2' : fields.float('Cuota IVA reducido', digits=(10,3)),
            'iva3' : fields.float('Cuota IVA super-reducido', digits=(10,3)),
            'importerecargo1' : fields.float('Cuota IVA normal', digits=(10,3)),
            'importerecargo2' : fields.float('Cuota IVA reducido', digits=(10,3)),
            'importerecargo3' : fields.float('Cuota IVA super-reducido', digits=(10,3)),
            'totaldocumento' : fields.float('Importe total del documento', digits=(10,3)),
            'importecobrado' : fields.float('Importe cobrado del documento', digits=(10,3)),
            'codmotivo' : fields.float('Motivo aplicado en documentos tipo 10', digits=(4,0)),
            'formapagoerp' : fields.char('Forma de pago en el ERP', size=20),
            'codproveedor': fields.float('Codigo de proveedor en venta indirecta', digits=(10,0)),
        }
    _defaults = {
            'fechadocumento' : datetime.now(),
            'tipodocumento' : 0,
            'docespecial' : 0,
            'codempresa' : 1,
            'codigoruta' : 1,
            'codvendedor' : 1,
            'codcliente' : 0,
            'coddireccion' : 0,
            'fechaentrega' : datetime.now(),
            'base1' : 0,
            'base2' : 0,
            'base3' : 0,
            'descuento' : 0,
            'descuentopp' : 0,
            'iva1' : 0,
            'iva2' : 0,
            'iva3' : 0,
            'importerecargo1' : 0,
            'importerecargo2' : 0,
            'importerecargo3' : 0,
            'totaldocumento' : 0,
            'importecobrado' : 0,
            'codmotivo' : 0,
            'codproveedor': 0,
        }
    
    
class tercap_import_lines(osv.osv):
    _name = 'tercap.import.lines'

    _columns = {
        'name' : fields.char(),
        'numdocumento' : fields.char('Num Documento',size=20),
        'fechadocumento' : fields.date('Fecha Documento'),
        'tipodocumento' : fields.float('Tipo Documento',digits=(3,0)),
        'numlinea': fields.float('Num de linea del documento',digits=(9,0)),
        'tipolinea' : fields.float('Tipo de linea',digits=(4,0)),
        'codproducto' : fields.float('codigo de producto',digits=(9,0)),
        'descripcion' : fields.char('Descripcion de la linea',size=50),
        'unidadventa' : fields.char('Unidad de venta del producto',size=10),
        'lote' : fields.char('Lote',size=20),
        'cantidad' : fields.float('Cantidad de venta en unidades',digits=(10,3)),
        'cajas': fields.float('Cantidad de venta en cajas',digits=(10,3)),
        'pesounidad' : fields.float('Peso unitario',digits=(10,3)),
        'pesototal' : fields.float('Peso total',digits=(10,3)),
        'precio' : fields.float('Precio bruto de venta por unidad',digits=(10,3)),
        'descuento1' : fields.float('Primer descuento en linea', digits=(10,3)),
        'descuento2' : fields.float('Segundo descuento en linea', digits=(10,3)),
        'precioneto' : fields.float('Precio neto de venta por unidad',digits=(10,3)),
        'preciomanual' : fields.boolean('Precio manual puesto por vendedor'),
        'iva' : fields.float('Porcentaje de iva',digits=(10,3)),
        'recargo' : fields.float('Porcentaje de R.E.',digits=(10,3)),
        'importeiva' : fields.float('Importe total de iva en la linea',digits=(10,3)),
        'importerecargo' : fields.float('Importe total de R.E. en la linea',digits=(10,3)),
        'codprovalternativo' : fields.char('Codigo producto alternativo TERCAP',size=20),
        'tipodescuento1' : fields.char('Tipo descuento en descuento1 % o P',size=3),
        'tipodescuento2' : fields.char('Tipo descuento en descuento2 % o P',size=3),
        'preciocoste' : fields.float('Precio de coste del producto',digits=(10,3)),
    }
    
    _defaults ={
        'fechadocumento' :  datetime.now(),
        'tipodocumento' : 0,
        'numlinea': 0,
        'tipolinea' : 1,
        'codproducto' : 0,
        'cantidad' : 0,
        'cajas' : 0,
        'pesounidad' : 0,
        'pesototal' : 0,
        'precio' : 0,
        'descuento1' : 0,
        'descuento2' : 0,
        'precioneto' : 0,
        'iva' : 0,
        'recargo' : 0,
        'importeiva' : 0,
        'importerecargo' : 0,
        'preciocoste' : 0,
    }

class tercap_import_payments(osv.osv):
    _name = 'tercap.import.payments'
    _columns = {
        'name' : fields.char(),
        'codcliente' : fields.float('Codigo de cliente en TERCAP', digits=(9,0)),
        'coddireccion' : fields.float('Codigo de direccion en TERCAP', digits=(9,0)),
        'numdocumento' : fields.char('Num Documento',size=20),
        'tipodocumento' : fields.float('Tipo Documento',digits=(3,0)),
        'fechadocumento' : fields.date('Fecha Documento'),
        'importedocum' : fields.float('Importe total del documento', digits=(10,3)),
        'importependiente' : fields.float('Importe pendiente de cobro', digits=(10,3)),
        'codcliealternativo' : fields.char('Codigo de cliente alternativo', size=20),
        'coddirealternativo' : fields.char('Codigo de direccion alternativo', size=20),
    }
    _defaults = {
        'codcliente' : 0,
        'coddireccion' :  0,
        'tipodocumento' : 1,
        'importedocum' : 0,
        'importependiente' : 0,
                 }
    
    @api.multi
    def sube_datos_cobros(self):
        os.chdir("/var/ftp/TERCAP")
        for nombre in glob.glob("COBRO*.txt"):
            f = open(nombre,'rU') 
            c = csv.reader(f, delimiter=';', skipinitialspace=True)
            for line in c:
                ref = fields.datetime.now()
                self.write({
                    'name': ref,
                    'codcliente': line[0],
                    'coddireccion': line[1],
                    'numdocumento':line[2],
                    'tipodocumento':line[3],
                    'fechadocumento':line[4],
                    'importedocum':line[5],
                    'importependiente':line[6],
                    'codlcliealternativo':line[7],
                    'coddirealternativo':line[8],
                })
            f.close()
    

class tercap_import_customers(osv.osv):
    _name = 'tercap.import.customers'

    _columns = {
        'name' : fields.char(),
        'codcliente' : fields.float('Codigo de cliente temporal en TERCAP', digits=(9,0)),
        'nombrefiscal' : fields.char('Nombre fiscal del cliente', size=50),
        'nombrecomercial' : fields.char('Nombre comercial del cliente', size=50),
        'direccion' : fields.char('Direccion fiscal del cliente', size=50),
        'poblacion' : fields.char('Poblacion fiscal del cliente', size=50),
        'cifnif' : fields.char('DNI/CIF/NIF del cliente', size=20),
        'codformapago' : fields.float('Indica si el cliente es de credito(0) o contado(1)',digits=(1,0)),
        'tipoiva' : fields.char('Como se aplica el iva al cliente', size=1),
        'observaciones' : fields.char('Observaciones', size=200),
        'id_ruta': fields.float('Id Ruta en TERCAP', digits=(3,0)),
        'codigo_postal':fields.char('C.P. del cliente', size=10),
        'telefono': fields.char('Telefono del cliente', size=20),
        'dia_descanso': fields.char('Dia de descanso del cliente', size=20),
        'tercap_reparto_id':fields.float('Id Reparto en TERCAP', digits=(4,0)),
    }
    _defaults = {
        'codformapago' : 0,
        'tipoiva': 'N',
                 }
    

    