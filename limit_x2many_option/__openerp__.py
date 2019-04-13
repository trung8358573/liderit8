# -*- coding: utf-8 -*-
{
    "name": "Limit list rows number",
    "version": "8.0.1.0.1",
    "category": "Extra Tools",
    "author": "Odoo Tools",
    "website": "https://odootools.com/apps/8.0/limit-list-rows-number-143",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "auto_install": False,
    "depends": [
        
    ],
    "data": [
        "data/data.xml",
        "views/template.xml",
        "security/ir.model.access.csv"
    ],
    "qweb": [
        
    ],
    "js": [
        
    ],
    "demo": [
        
    ],
    "external_dependencies": {},
    "summary": "Let assign default value to limit number of rows in list views through xml",
    "description": """
    The app is a tool to limit number of lines in lists (one2many, many2many) by default

    Standard Odoo opens 80 rows, but using the tree attribute<i>'limit_list'</i> you may assign any number
    It simplifies form views, since you do not have to scroll a lot
    You may switch to the next page by usual Odoo 'arrow' buttons
    You need the attribute to a tag tree:<i>"limit_list='15'"</i>. Observe the example in the 'Documentation' section to use it in your own modules.
""",
    "images": [
        "static/description/main.png"
    ],
    "price": "0.0",
    "currency": "EUR",
}