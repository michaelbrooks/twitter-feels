/**
 * A view for rendering a tray of thermometers.
 *
 * Created by mjbrooks on 3/15/14.
 */
(function (win) {

    var views = win.namespace.get('thermometer.views');
    var libs = win.namespace.get('libs');

    var logger = libs.Logger.get('thermometer.views.tray_view');

    views.TrayView = views.CommonView.extend({

        className: 'tray-view',

        initialize: function(options) {
            //All the thermometer views
            this.views = [];
            //Views by model id
            this.view_lookup = {};

            this.listenTo(this.collection, 'add', this.feeling_added);
            this.listenTo(this.collection, 'remove', this.feeling_removed);

            logger.debug('initialized', options);
        },

        feeling_added: function(model) {
            var view = new views.ThermometerView({
                model: model
            });

            this.views.push(view);
            this.view_lookup[model.id] = view;

            this.$el.append(view.render().el);

            logger.debug('feeling added', model.id);
        },

        feeling_removed: function(model) {

            var view = this.view_lookup[model.id];
            view.remove();

            //Remove the view from the list
            var i = this.views.indexOf(view);
            this.views.splice(i, 1);

            //Remove from the map
            delete this.view_lookup[model.id];

            logger.debug('feeling removed', model.id);
        }
    });


})(window);