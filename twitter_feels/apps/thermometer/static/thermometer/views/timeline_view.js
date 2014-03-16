/**
 * View for showing timelines.
 *
 * Created by mjbrooks on 3/15/14.
 */
(function (win) {

    var views = win.namespace.get('thermometer.views');
    var libs = win.namespace.get('libs');

    var logger = libs.Logger.get('thermometer.views.timeline_view');

    views.TimelineView = views.CommonView.extend({

        className: 'timeline-view',

        template: _.template($('#timeline-view-template').html()),

        ui: {
            svg: 'svg'
        },

        initialize: function(options) {
            //Expects the collection to be a collection of tweet groups with a feeling

            this.has_rendered = false;
            this.listenTo(this.collection, 'change', this.render);

            logger.debug('initialized', options);
        },

        render: function() {

            if (!this.has_rendered) {
                logger.debug('running template...');

                //Make some skeleton HTMl with an underscore template
                this.$el.html(this.template(this.collection.toJSON()));

                this.bindUIElements();

                this.has_rendered = true;
            }

            //Then do the d3 bind/enter/exit/update thing
            var svg = d3.select(this.ui.svg[0]);

            svg.append('rect').attr('width', 100).attr('height', 200);

            logger.debug('rendered');

            return this;
        }
    });

})(window);