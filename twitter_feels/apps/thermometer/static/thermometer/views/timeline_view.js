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
        right: 10,
        bottom: 30,
        left: 50
    };

    var skip_window_size = 9;

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

            this.listenTo(this.collection, 'change', this.render);

            this.xScale = d3.time.scale();
            this.yScale = d3.scale.linear();

            this.xAxis = d3.svg.axis()
                .scale(this.xScale)
                .ticks(4)
                .orient("bottom");

            var formatPercent = d3.format(".0%");
            this.yAxis = d3.svg.axis()
                .scale(this.yScale)
                .orient("left")
                .ticks(4)
                .tickFormat(formatPercent);


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

                var inner = d3.select(this.ui.svg[0]).append("g")
                    .attr('class', 'inner')
                    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

                inner.append("g")
                    .attr("class", "x axis");

                inner.append("g")
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
            var height = this.$el.height() - 5;

            var svg = d3.select(this.ui.svg[0])
                .attr('width', width)
                .attr('height', height);

            var innerWidth = width - margin.left - margin.right;
            var innerHeight = height - margin.top - margin.bottom;

            this.xScale.range([0, innerWidth]);
            this.yScale.range([innerHeight, 0]);

            this.xScale.domain([this.update.intervals.recent.get('start'), this.update.intervals.recent.get('end')])
            this.yScale.domain([-1, 1]);

            var data = this.collection.models.slice(skip_window_size);

            this.color.domain(data.map(function(d) {
                return d.get('word');
            }));

            var inner = svg.select('g.inner');

            var group_bind = inner.selectAll("g.timeline-group")
                .data(data);

            var group_enter = group_bind.enter()
                .append('g')
                .attr('class', 'timeline-group')
                .append('path')
                .attr('class', 'line');

            var group_exit = group_bind.exit()
                .remove();

            var self = this;

            inner.select('g.y.axis')
                .transition()
                .duration(1500)
                .call(this.yAxis);

            inner.select('g.x.axis')
                .attr("transform", "translate(0," + innerHeight + ")")
                .transition()
                .duration(1500)
                .call(this.xAxis);

            group_bind.select('path.line')
                .style("stroke", function(g) {
                    return self.color(g.get('word'));
                })
                .transition()
                .duration(1500)
                .attr("d", function(g) {
                    return self.line(g.get('recent_series'));
                });

        }
    });

})(window);