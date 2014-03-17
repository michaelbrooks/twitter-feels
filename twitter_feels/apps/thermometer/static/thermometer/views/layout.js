/**
 * Describes the layout of the thermometer app.
 *
 * Created by mjbrooks on 3/15/14.
 */
(function (win) {

    var views = win.namespace.get('thermometer.views');

    views.ThermometerLayout = views.CommonView.extend({

        el: '.thermometer-app',

        ui: {
            tray: '.tray',
            tray_description: '.thermometer-panel .description',
            timelines: '.timelines',
            timelines_description: '.timeline-panel .description',
            adder: '.adder .plus'
        },

        events: {
            'click .adder .plus': 'adder_clicked'
        },

        initialize: function(options) {
            this.update = options.update;

            this.bindUIElements();
        },

        /**
         * Renders a view into one of the layout regions.
         *
         * @param name
         * @param view
         */
        show: function(name, view) {
            if (!_.has(this.ui, name)) {
                throw "Unknown region " + name;
            }

            var region = this.ui[name];

            if (region.view) {
                region.view.remove();
            }

            region.html(view.render().el);
            region.view = view;
        },

        adder_clicked: function() {
            this.update.trigger('show-feeling-list');
        }

    });

})(window);