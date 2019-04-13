# -*- encoding: utf-8 -*-
{
    'name': 'Secuencias en Clientes',
    'version': '0.1',
    'category': 'Other',
    'summary': """Secuencias para la referencia interna en clientes""",
    'description': """Secuencias para la referencia interna en clientes""",
    'author': 'LiderIT',
    'depends': ['base'],
    'init_xml': [],
    'data': [
        'security/ir.model.access.csv',
        'res_partner_view.xml',
    ],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
