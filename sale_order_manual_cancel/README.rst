.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

=======================
Sale order manual cancel
=======================

This module allows to force manually ending of sale orders.
The wizard will raise an error. 
- If the order is in state 'draft' or 'cancel'.
- If the order has some picking not finished (done or cancel).
- If the order has some invoice not finished (paid or cancel).

Credits
=======

Contributors
------------
* AvanzOSC
* LiderIT
