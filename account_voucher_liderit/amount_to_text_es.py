# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################

from openerp.osv import osv,fields
from openerp.tools.translate import _
import logging

_logger = logging.getLogger(__name__)

#-------------------------------------------------------------
#SPANISH
#-------------------------------------------------------------

_n1 = ( "un","dos","tres","cuatro","cinco","seis","siete","ocho",
        "nueve","diez","once","doce","trece","catorce","quince",
        "dieciseis","diecisiete","dieciocho","diecinueve","veinte")

_n11 =( "un","dos","tres","cuatro","cinco","seis","siete","ocho","nueve")

_n2 = ( "dieci","veinti","treinta","cuarenta","cincuenta","sesenta",
        "setenta","ochenta","noventa")

_n3 = ( "ciento","dosc","tresc","cuatroc","quin","seisc",
        "setec","ochoc","novec")


def _numerals(n):
    _logger.error('##### AIKO ###### Amount to text recibe como valor %s'%n)
    cRes=''
    # Localizar los billones    
    prim,resto = divmod(n,10L**12)
    if prim!=0:
        _logger.error('##### AIKO ###### Amount to text entra en billones %s'%n)
        if prim==1:     cRes = "Un billon"
        else:           cRes = _numerals(prim,0)+" billones" # Billones es masculino

        if resto!=0:    cRes = " "+_numerals(resto)

    else:
    # Localizar millones
        prim,resto = divmod(n,10**6)
        if prim!=0:
            _logger.error('##### AIKO ###### Amount to text entra en millones con resto%s'%resto)
            if prim==1: cRes = "Un millón"
            else:       cRes= _numerals(prim)+" millones" # Millones es masculino

            if resto!=0: cRes += " "+  _numerals(resto)

        else:
    # Localizar los miles
            prim,resto = divmod(n,10**3)
            if prim!=0:
                _logger.error('##### AIKO ###### Amount to text entra en miles con prim %s'%prim)
                _logger.error('##### AIKO ###### Amount to text entra en miles con resto %s'%resto)
                if prim==1:
                    if cRes=='': cRes="Mil"
                    else: cRes+="mil"
                else: 
                    if cRes=='':  cRes=_numerals(prim)+" mil"
                    else: cRes += " "+  _numerals(prim)+" mil"

                if resto!=0: 
                    cRes += " "+  _numerals(resto)
                    
                _logger.error('##### AIKO ###### Amount to text salgo de miles %s'%cRes)
            else:
    # Localizar los cientos
                prim,resto=divmod(n,100)
                if prim!=0:
                    _logger.error('##### AIKO ###### Amount to text entra en cientos con prim %s'%prim)
                    _logger.error('##### AIKO ###### Amount to text entra en cientos con resto %s'%resto)
                    if prim==1:
                        if resto==0: 
                            if cRes=='': cRes="Cien"
                            else: cRes+="cien"
                        else:     
                            if cRes=='': cRes="ciento"
                            else: cRes+="ciento"
                    else:
                        if cRes=='': cRes=_n3[prim-1]+"ientos"
                        else: cRes+=_n3[prim-1]+"ientos"


                    if resto!=0:  cRes+=" "+_numerals(resto)
                    _logger.error('##### AIKO ###### Amount to text salgo de cientos con %s'%cRes)
                else:
    # Localizar las decenas
                    if n==1:              cRes="un"
                    elif n<=20:   
                        if cRes=='':  cRes=_n1[n-1]
                        else:cRes+=_n1[n-1]
                    else:
                        prim,resto=divmod(n,10)
                        _logger.error('##### AIKO ###### Amount to text entra en mas de 20 con prim %s'%prim)
                        _logger.error('##### AIKO ###### Amount to text entra en mas de 20 con resto %s'%resto)
                        if cRes=='': cRes=_n2[prim-1]
                        else: cRes+=_n2[prim-1]
                        
                        if resto!=0:
                            if prim==2: 
                                if cRes=='': cRes=_n11[resto-1]
                                else: cRes+=_n11[resto-1]
                            else: 
                                cRes+=" y "+_n1[resto-1]

                        #if resto==1:  cRes=""
                        _logger.error('##### AIKO ###### Amount to text saldo de uds %s'%cRes)

    return cRes

def spanish_number(val):
    # Nos aseguramos del tipo de <nNumero>
    # se podría adaptar para usar otros tipos (pe: float)
    nNumero = long(val)

    if nNumero<0:       cRes = "menos "+_numerals(-nNumero)
    elif nNumero==0:    cRes = "cero"
    else:               cRes = _numerals(nNumero)

    # Excepciones a considerar
    #if nNumero%10 == 1 and nNumero%100!=11:
    #    cRes = "o"
    capital = cRes[0].capitalize()
    cRes = capital + cRes[1:]
    return cRes

def amount_to_text(number, currency):
    number = '%.2f' % number
    units_name = currency
    list = str(number).split('.')
    start_word = spanish_number(int(list[0]))
    end_word = spanish_number(int(list[1]))
    units_number = int(list[0])
    units_name = (units_number > 1) and units_name+'s ' or units_name+' '
    cents_number = int(list[1])
    cents_name = (cents_number > 1) and 'Cents.' or 'Cent.'

    final_result = start_word +' '+units_name+ end_word +' '+cents_name
    return final_result
