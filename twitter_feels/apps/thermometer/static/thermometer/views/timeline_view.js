/**
 * View for showing timelines.
 *
 * Created by mjbrooks on 3/15/14.
 */
(function (win) {

    var views = win.namespace.get('thermometer.views');
    var libs = win.namespace.get('libs');

    var logger = libs.Logger.get('thermometer.views.timeline_view');

    var margin = {
        top: 20,
        left: 20
    };

    views.TimelineView = views.CommonView.extend({

        className: 'timeline-view',

        template: _.template($('#timeline-view-template').html()),

        ui: {
            svg: 'svg'
        },

        initialize: function (options) {
            //Expects the collection to be a collection of tweet groups with a feeling
            this.update = options.update;

            this.has_rendered = false;

            this.listenTo(this.collection, 'add remove change', this.render);


            this.xScale = d3.time.scale();
            this.yScale = d3.scale.linear();

            this.xAxis = d3.svg.axis()
                .scale(this.xScale)
                .orient("bottom");

            this.yAxis = d3.svg.axis()
                .scale(this.xScale)
                .orient("left");

            var self = this;

            var _movingSum;

            this.line = d3.svg.line()
                .interpolate("basis")
                .x(function (d) {
                    return self.xScale(d.start_time);
                })
                .y(function (d) {
                    return self.yScale(d.percent_change_smoothed);
                });

            this.color = d3.scale.category10();

            logger.debug('initialized', options);
        },

        render: function () {

            if (!this.has_rendered) {
                logger.debug('running template...');

                //Make some skeleton HTMl with an underscore template
                this.$el.html(this.template(this.collection.toJSON()));

                this.bindUIElements();

                var top = d3.select(this.ui.svg[0]).append("g")
                    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

                top.append("g")
                    .attr("class", "x axis");

                top.append("g")
                    .attr("class", "y axis");

                this.has_rendered = true;
            }

            var self = this;

            //Delay rendering
            setTimeout(function () {
                self.delayed_render();

                logger.debug('rendered');
            }, 1);

            return this;
        },

        delayed_render: function () {

            var width = this.$el.width();
            var height = this.$el.height();

            var svg = d3.select(this.ui.svg[0])
                .attr('width', width)
                .attr('height', height);

            svg.select('g.y.axis')
                .call(this.yAxis);

            svg.select('g.x.axis')
                .attr("transform", "translate(0," + height + ")")
                .call(this.xAxis);

            this.xScale.range([0, width]);
            this.yScale.range([height, 0]);

            var data = this.collection.models;

            this.color.domain(data.map(function(d) {
                return d.get('word');
            }));

            this.xScale.domain([this.update.intervals.recent.get('start'), this.update.intervals.recent.get('end')])
            this.yScale.domain([-1, 1]);

            var group_bind = svg.selectAll("g.timeline-group")
                .data(data);

            var group_enter = group_bind.enter()
                .append('g')
                .attr('class', 'timeline-group')
                .append('path')
                .attr('class', 'line');

            var group_exit = group_bind.exit()
                .remove();

            var self = this;

            group_bind.select('path.line')
                .attr("d", function(g) {
                    return self.line(g.get('recent_series'));
                })
                .style("stroke", function(g) {
                    return self.color(g.get('word'));
                });

        }
    });

})(window);