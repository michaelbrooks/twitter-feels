/**
 * A view for rendering a tray of thermometers.
 *
 * Created by mjbrooks on 3/15/14.
 */
(function (win) {

    var views = win.namespace.get('thermometer.views');
    var utils = win.namespace.get('thermometer.utils');
    var libs = win.namespace.get('libs');

    var logger = libs.Logger.get('thermometer.views.tray_view');

    var FEELINGS_LIMIT = 9;
    var colorScale = libs.d3.scale.category10();

    views.TrayView = views.CommonView.extend({

        className: 'tray-view',
        template: _.template($('#tray-view-template').html()),

        ui: {
            tray: '.tray',
            plus: '.plus'
        },

        events: {
            'click .adder .plus': 'adder_clicked',
            'click .thermometer-view .minus': 'minus_clicked'
        },

        initialize: function(options) {
            this.update = options.update;

            //All the thermometer views
            this.views = [];
            //Views by model id
            this.view_lookup = {};

            this.listenTo(this.collection, 'add', this.feeling_added);
            this.listenTo(this.collection, 'remove', this.feeling_removed);

            logger.debug('initialized', options);
        },

        render: function() {
            this.$el.html(this.template());
            this.bindUIElements();

            this.ui.plus.tooltip({
                placement: 'top'
            });

            return this;
        },

        adder_clicked: function() {
            this.update.trigger('show-feeling-list');
        },

        minus_clicked: function(e) {
            var feeling_id = $(e.target).data('id');
            this.update.remove_feeling(feeling_id);
        },

        feeling_added: function(model) {
            var view = new views.ThermometerView({
                model: model
            });

            this.views.push(view);
            this.view_lookup[model.id] = view;

            var index = this.views.length - 1;
            view.set_color(colorScale(index));

            this.ui.tray.append(view.render().el);

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

            //Re-render all the feelings
            _.each(this.views, function(v, index) {
                v.set_color(colorScale(index));
                v.render();
            });

            logger.debug('feeling removed', model.id);
        }
    });


})(window);