# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Customer Wallet For Website And POS',
    'version': '12.0.0.3',
    'author': 'BrowseInfo',
    'website' : 'www.browseinfo.in',
    'depends': ['base','sale_management','account','website','website_sale','point_of_sale'],
    'summary': 'This apps helps to use Wallet on website and POS, pay order using wallet balance',
    'description': """Website Wallet

        Wallet on website and POS, pay order using wallet balance
        eCommerce Wallet payment
        payment using wallet
        wallet balance.
        shop Wallet payment
        website wallet payment
        payment wallet
        payment on website using wallet
        wallet payment method
        Wallet on website and pay order using wallet balance
        eCommerce Wallet payment
        payment using wallet
        wallet balance.
        shop Wallet payment
        website wallet payment
        payment wallet
        payment on website using wallet
        wallet payment method
        

        POS Customer Wallet Management
        POS Wallet Management
        point of sale Wallet Management
        point of sales Wallet management
        Customer Wallet payment with POS
        Customer wallet POS
        customer credit POS
        POS customer credit payment    
        POS Customer Wallet payment Management
        POS Wallet payment Management
        point of sale Wallet payment Management
        point of sales Wallet payment management
        wallet on POs
        wallet on point of sale
This Module allow the seller to recharge wallet for the customer. 
    POS Customer Wallet Management
    POS Wallet Management
    point of sale Wallet Management
    point of sales Wallet management
    Customer Wallet payment with POS
    Customer wallet POS
    customer credit POS
    POS customer credit payment    
    POS Customer Wallet payment Management
    POS Wallet payment Management
    point of sale Wallet payment Management
    point of sales Wallet payment management
    wallet on POs
    wallet on point of sale

        
        
""" ,
    'category': 'eCommerce',
    "price": 149,
    "currency": 'EUR',
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/wallet.xml',
        'views/template.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'images':['static/description/Banner.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
