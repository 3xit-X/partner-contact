# Copyright 2012 Camptocamp SA - Yannick Vaucher
# Copyright 2017 Tecnativa - Vicent Cubells
# Copyright 2018 brain-tec AG - Raul Martin
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Res Partner Affiliates",
    "version": "14.0.2.29",
    "description": "Manage Partner Affiliates",
    "summary": "",
    "author": "",
    "website": "https://www.gruppochiarcosso.com",
    "license": "LGPL-3",
    "category": "Human Resources",
    "depends": ["base"],
    "data": [
        # Views
        "views/res_partner_view.xml"
    ],
    "post_init_hook": "contact_type_post_init_hook",
    "uninstall_hook": "contact_type_uninstall_hook",
    "installable": True,
}
