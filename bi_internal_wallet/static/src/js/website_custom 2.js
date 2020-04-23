odoo.define('bi_internal_wallet.odoo_website_wallet', function(require) {
    "use strict";
    var core = require('web.core');
    var _t = core._t;

    var ajax = require('web.ajax');
    $(document).ready(function() {
        var oe_website_sale = this;
        
        var $wallet = $("#website_wallet");
        $wallet.click(function () {
            if ($(this).is(':checked')) {
                var wallet = $(this).is(':checked');
                
                ajax.jsonRpc('/shop/payment/wallet', 'call', {
                    'wallet': wallet,
                }).then(function (wallet) {
                    location.reload();
                });
                
            } else {
                //Do Nothing
            }
        });
    });
});;
