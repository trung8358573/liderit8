openerp.limit_x2many_option = function (instance) {

var _t = instance.web._t,
   _lt = instance.web._lt;
var QWeb = instance.web.qweb;


instance.web.ListView.include({
    limit: function () {
        if (this._limit === undefined) {
            if (this.fields_view.arch.attrs.limit_list) {
                this._limit = parseInt(this.fields_view.arch.attrs.limit_list);
            }

            else {
                this._limit = (this.options.limit
                            || this.defaults.limit
                            || (this.getParent().action || {}).limit
                            || 80);
            }
        }
        return this._limit;
    },

});

};