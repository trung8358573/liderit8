from openerp.osv import osv, fields
from openerp import api
import logging
_logger = logging.getLogger(__name__)

class ruta(osv.osv):
    _name = "ruta"
    _description = "identificador de ruta para repartos"
    _columns = {
        
         'descripcion':fields.char('Descripcion', size=50, required = True ), 
         #28-3-16 agregamos codigo para exportar a Tercap
         'cod_tercap': fields.integer ('Codigo de Ruta para Tercap', required = True ),
         'tipo': fields.selection([  
            ('R', 'Reparto'),
            ('A', 'Autoventa'),                            
            ('M', 'Mixta'),
            ('P', 'Preventa'),
            ('T', 'Televenta'),
            ], 'Tipo ruta:'),
        'cod_vendedor': fields.many2one("res.partner", "Vendedor"),
        'cod_equipo': fields.many2one("crm.case.section", "Equipo de ventas"),
        'journal_id': fields.many2one("account.journal", "Diario para Facturas"),  
        'clave_config':fields.char('Contrasena Entrada', size=10 ), 
        'permitir_venta_lotes': fields.selection([  
            ('S', 'Si'),
            ('N', 'No'),                            
            ], 'Permitir venta por lotes:'),
        'permitir_venta_cajas': fields.selection([  
            ('S', 'Si'),
            ('N', 'No'),                            
            ], 'Permitir venta cajas:'),       
        'cajas_por_defecto': fields.selection([  
            ('S', 'Si'),
            ('N', 'No'),                            
            ], 'Cajas por defecto:'),               
        'Permitir_cambio_precio': fields.selection([  
            ('S', 'Si'),
            ('N', 'No'),                            
            ], 'Permitir Cambio Precio:'),                   
        'aviso_riesgo': fields.selection([  
            ('S', 'Si'),
            ('N', 'No'),                            
            ], 'Aviso de Riesgo:'),  
        'permitir_cambio_pago': fields.selection([  
            ('S', 'Si'),
            ('N', 'No'),                            
            ], 'Permitir Cambio de Pago:'), 
        'aplicar_dto_sincab': fields.selection([  
            ('S', 'Si'),
            ('N', 'No'),                            
            ], 'Aplican descuentos en pie para documentos sin cabecera:'),                                                    
        'permitir_cliente_nuevo': fields.selection([  
            ('S', 'Si'),
            ('N', 'No'),                            
            ], 'Permite crear clientes nuevos:'), 
        'permite_cambio_vendedor': fields.selection([  
            ('S', 'Si'),
            ('N', 'No'),                            
            ], 'Permite cambiar de vendedor:'),                
        'aplicar_cond_retiradas': fields.selection([  
            ('S', 'Si'),
            ('N', 'No'),                            
            ], 'Indica sise aplican las condiciones de descuento en la retirada de mercancia:'),                         
        'pedir_lote_retiradas': fields.selection([  
            ('S', 'Si'),
            ('N', 'No'),                            
            ], 'Indica si se solicitara el lote en la aplicacion del terminal al hacer una retirada:'),                          
        'permitir_cobros': fields.selection([  
            ('S', 'Permite gestionar cobros'),
            ('N', 'No permite'),
            ('Z', 'Permite cobros y prohibe vender'),                           
            ], 'Indica valores posibles para este permiso:'),  
        'ecotasa_en_precio': fields.selection([  
            ('S', 'Si'),
            ('N', 'No'),                            
            ], 'Indica si la ecotasaya va incluida en el precio del producto:'),                 
        'ecotasa_en_regalos': fields.selection([  
            ('S', 'Si'),
            ('N', 'No'),                            
            ], 'Indica si debe aplicarse ecotasa en lineas de regalo:'),
        'ecotasa_sin_cab': fields.selection([  
            ('S', 'Si'),
            ('N', 'No'),                            
            ], 'Indica si debe aplicarse ecotasa en documentos sin cabecera:'),                    
        'perguntar_tipo_doc': fields.selection([  
            ('S', 'Si'),
            ('N', 'No'),                            
            ], 'Indica si se pregunta siempre al final de la venta el tipo de documento que va a crear:'),  
        'pedir_peso_en_linea': fields.selection([  
            ('S', 'Si,  en cada linea '),
            ('N', 'No, al final de la venta'),                            
            ], 'Para productos de peso variable, indica si la aplicacion pedira el peso en cada linea:'),            
        'permitir_venta_sin_stock': fields.selection([  
            ('S', 'Si '),
            ('N', 'No'),                            
            ], 'Indica si se permite la venta aunque no haya stock suficiente:'),            
        'permitir_descarga_parcial': fields.selection([  
            ('S', 'Si '),
            ('N', 'No'),                            
            ], 'Indica si se permite realizar descargas parciales:'),                          
        'imprimir_albaran_con_iva': fields.selection([  
            ('S', 'Si '),
            ('N', 'No'),                            
            ], 'Indica si los albaranes se imprimen con impuestos:'),               
        'imprimir_cabecera': fields.selection([  
            ('S', 'Si '),
            ('N', 'No'),                            
            ], 'Indica si se imprimen los datos de la empresa en la cabecera del documento:'),   
        'imprimir_corregido': fields.selection([  
            ('S', 'Si '),
            ('N', 'No'),                            
            ], 'Indica si al corregir un documento, se imprimira una copia del original:'),        
        'imprimir_anulado': fields.selection([  
            ('S', 'Si '),
            ('N', 'No'),                            
            ], 'Indica si al anular un documento, se imprimira una copia con un texto ANULADO:'),
        'orden_productos': fields.selection([  
            ('N', 'Ordenados por codigo de productos'),
            ('L', 'Mismo orden en el que se han vendido'),                            
            ], 'Indica el orden en elque se imprimen los productos:'),        
                
        'es_proveedor_mayorista': fields.selection([  
            ('N', 'No '),
            ('S', 'Si'),                            
            ], 'Indica si la ruta la realiza un proveedor mayorista:'),          
        'cod_proveedor': fields.many2one("res.partner", "Proveedor si la ruta es proveedor mayorista"),
        'tercap_incluir': fields.boolean('Activa en Tercap'), 
        'partner_rutas_ids':fields.one2many('res.partner', 'tercap_ruta_id', 'Clientes'),
        'dias_visita': fields.selection([  
            ('1', 'Lunes'),
            ('2', 'Martes'),
            ('3', 'Miercoles'),
            ('4', 'Jueves'),
            ('5', 'Viernes'),
            ('6', 'Sabados'),
            ('7', 'Domingos'),
            ('99', 'Sin dia'),                            
            ], 'Dias de visita:'),    
        'orden_visita': fields.integer('Orden de visita dentro del dia:'),  
        'frecuencia': fields.selection([  
            ('S', 'Semanal'),
            ('P', 'Quincenal Par'),
            ('I', 'Quincenal Impar'),                  
            ], 'Frecuencia de visitas:'),
        'active': fields.boolean('Activa'),                                                                
         }
    _defaults = {
        'tipo':'R',         
        'permitir_venta_lotes':'S',
        'permitir_venta_cajas':'S',
        'cajas_por_defecto': 'N',
        'Permitir_cambio_precio': 'S',
        'aviso_riesgo': 'N',
        'permitir_cambio_pago':'S',
        'aplicar_dto_sincab': 'N',
        'permitir_cliente_nuevo': 'S',
        'permite_cambio_vendedor': 'S',
        'aplicar_cond_retiradas': 'S',
        'pedir_lote_retiradas': 'N',
        'permitir_cobros': 'S',
        'ecotasa_en_precio': 'N',
        'ecotasa_en_regalos': 'N',
        'ecotasa_sin_cab': 'N',
        'perguntar_tipo_doc': 'N', 
        'pedir_peso_en_linea': 'S',
        'permitir_venta_sin_stock': 'S',
        'permitir_descarga_parcial': 'S',
        'imprimir_albaran_con_iva': 'S',
        'imprimir_cabecera': 'S',
        'imprimir_corregido': 'N',
        'imprimir_anulado': 'N', 
        'orden_productos': 'N',
        'es_proveedor_mayorista': 'N',
        'tercap_incluir': True,
        'dias_visita': '99',
        'orden_visita': 1,
        'frecuencia': 'S',
        'active': True,
        } 
    _rec_name = 'descripcion'
    _order = 'descripcion'