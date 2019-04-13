.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License

Invoice numbering without gaps
==============================
There shall be no gaps in invoice numbering. 
Use this module to recover invoice numbers from cancelled invoices.

This is especially useful when you would like to issue a new invoice that stems from a new sales order and assign it a number from some cancelled invoice.
Remember that the invoice date is also transferred.

Usage
=====
There is a new button "Reuse cancelled invoice number" on the invoice form.
It is visible only if:

- there is any cancelled invoice with nonempty internal_number,
- invoice is in draft state.

The button triggers a wizard with a list of cancelled invoices that have their internal_number field set.
After the user makes a selection, its number and date will be used as the number and the date for the current invoice.





