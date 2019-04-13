{
    "name": "sale_order_invisible_for_customer",
    "version": "1.1",
    "depends": ['base', 'sale'],
    "author": "Lider IT",
    "category": "Sales",
    "description": """	realizar presupuestos de pedidos de venta delante del cliente """,
    "website":'http://www.liderit.es',
   
    "init_xml": [],
    'update_xml': [
               'views/sale_order_view.xml',
                   ],
#     'data': ['workflow/workflow.xml'],
    'demo_xml': [],
#     'data': ['general_data.xml'],
    'installable': True,
	'active': False,
}   
