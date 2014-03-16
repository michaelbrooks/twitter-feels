/**
 * An enhanced Backbone.View subclass -- borrows some stuff from Marionette.
 *
 * Created by mjbrooks on 3/15/14.
 */
(function (win) {

    var views = win.namespace.get('thermometer.views');
    var libs = win.namespace.get('libs');

    views.CommonView = libs.Backbone.View.extend({

        // This method binds the elements specified in the "ui" hash inside the view's code with
        // the associated jQuery selectors.
        bindUIElements: function(){
            if (!this.ui) { return; }

            // store the ui hash in _uiBindings so they can be reset later
            // and so re-rendering the view will be able to find the bindings
            if (!this._uiBindings){
                this._uiBindings = this.ui;
            }

            // get the bindings result, as a function or otherwise
            var bindings = _.result(this, "_uiBindings");

            // empty the ui so we don't have anything to start with
            this.ui = {};

            // bind each of the selectors
            _.each(_.keys(bindings), function(key) {
                var selector = bindings[key];
                this.ui[key] = this.$(selector);
            }, this);
        }

    });

})(window);