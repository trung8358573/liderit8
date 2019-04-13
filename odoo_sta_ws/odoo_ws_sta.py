# -*- coding: utf-8 -*-

from openerp import models, api
from openerp.osv import fields, osv

from openerp.tools import (
    drop_view_if_exists,
)


# Consulta para mostrar Clientes visibles
class tabla_visibles_aristos(osv.osv):
	_name = 'tabla.visibles.aristos'

   	_auto = False

	_columns = {
		'id': fields.integer('id', readonly=True),
		'nombre': fields.char('Nombre comercial', readondly=True),
		'direccion': fields.char('Dirección', readondly=True),
		'poblacion': fields.char('Población', readondly=True),
		'email': fields.char('Correo electrónico', readondly=True),
		'codigo_postal': fields.char('Código postal', readondly=True),
	}

	def init(self, cr):

		drop_view_if_exists(cr, 'tabla_visibles_aristos')

		cr.execute("""
		  CREATE OR REPLACE VIEW tabla_visibles_aristos AS(
		  SELECT 
		  partner.id as id,
		  partner.comercial as nombre,
          partner.street as direccion,
          partner.city as poblacion,
          partner.email as email,
          partner.zip as codigo_postal
          from res_partner as partner
          where not partner.no_visible_aristos=True and partner.customer)
		""")

