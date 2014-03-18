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
        right: 50,
        bottom: 50,
        left: 50
    };

    var percent_range = [-0.5, 0.5];

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

            var formatPercent = d3.format("+.0%");
            var normPercent = function(value) {
                if (value == 0) {
                    return 'Norm';
                } else {
                    return formatPercent(value);
                }
            };
            this.yAxis = d3.svg.axis()
                .scale(this.yScale)
                .orient("left")
                .ticks(3)
                .tickFormat(normPercent);

            this.yAxisRight = d3.svg.axis()
                .scale(this.yScale)
                .orient("right")
                .ticks(3)
                .tickFormat(normPercent);

            var self = this;

            this.line = d3.svg.line()
                .interpolate("basis")
                .x(function (d) {
                    return self.xScale(d.start_time);
                })
                .y(function (d) {
                    if (self.init_line) {
                        return self.yScale(0);
                    } else {
                        return self.yScale(d.percent_change_smoothed);
                    }
                });

            this.color = d3.scale.category10();

            logger.debug('initialized', options);
        },

        render: function () {


            var self = this;

            if (!this.has_rendered) {
                this.initial_render();
                this.has_rendered = true;
            }

            //Delay rendering
            setTimeout(function () {
                self.delayed_render();
            }, 1);

            return this;
        },

        initial_render: function() {
            logger.debug('initial render...');

            //Make some skeleton HTMl with an underscore template
            this.$el.html(this.template(this.collection.toJSON()));

            this.bindUIElements();

            this.svg = d3.select(this.ui.svg[0]);

            this.inner = this.svg.append("g")
                .attr('class', 'inner')
                .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

            this.inner.append("g")
                .attr("class", "x axis");

            this.inner.append("g")
                .attr("class", "y axis");

            this.inner.append("g")
                .attr("class", "y axis right");

            this.chart = this.inner.append('svg')
                .attr('class', 'chart');

            this.chart.append('line')
                .attr('class', 'baseline');
        },

        delayed_render: function () {

            var size = {
                width: this.$el.width(),
                height: this.$el.height() - 5
            };

            var inner_size = {
                width: size.width - margin.left - margin.right,
                height: size.height - margin.top - margin.bottom
            };

            this.resize_svg(size, inner_size);
            this.update_scales(inner_size);
            this.update_axes(inner_size);
            this.update_baseline(inner_size);

            this.update_feeling_groups();

//            group_bind
//                .data(function(timeline_group) {
//                    return timeline_group.examples;
//                });


            if (!this.has_rendered_data && this.collection.size()) {
                this.has_rendered_data = true;
                logger.debug('rendered first data');
            }

            logger.debug('rendered');
        },

        update_scales: function(inner_size) {
            this.xScale.range([0, inner_size.width]);
            this.yScale.range([inner_size.height, 0]);

            var end_time = this.update.intervals.recent.get_last_start_time();
            var timedomain = [this.update.intervals.recent.get('start'), end_time];

            this.xScale.domain(timedomain);
            this.yScale.domain(percent_range);

            this.color.domain(this.collection.models.map(function(d) {
                return d.get('word');
            }));
        },

        resize_svg: function(size, inner_size) {
            this.svg.attr('width', size.width)
                .attr('height', size.height);


            this.chart.attr('width', inner_size.width)
                .attr('height', inner_size.height)
        },

        transition_duration: function() {
            if (!this.has_rendered_data) {
                return 1500;
            }
            return 250;
        },

        update_axes: function(inner_size) {

            this.inner.select('g.y.axis')
                .call(this.yAxis);

            this.inner.select('g.y.axis.right')
                .attr('transform', 'translate(' + inner_size.width + ', 0)')
                .call(this.yAxisRight);

            this.inner.select('g.x.axis')
                .attr("transform", "translate(0," + inner_size.height + ")")
                .transition()
                .duration(this.transition_duration())
                .call(this.xAxis);
        },

        update_baseline: function(inner_size) {
            this.chart.select('line.baseline')
                .attr('x1', 0)
                .attr('x2', inner_size.width)
                .attr('y1', this.yScale(0))
                .attr('y2', this.yScale(0));
        },

        feeling_group_enter: function(enter) {
            var self = this;

            var group_enter = enter.append('g')
                .attr('class', 'timeline-group');

            //Make lines get initialized to 0
            this.init_line = true;

            group_enter.append('path')
                .attr('class', 'line')
                .style('opacity', 0)
                .attr("d", function(g) {
                    return self.line(g.get('recent_series').slice(skip_window_size));
                });

            this.init_line = false;

            group_enter.append('g')
                .attr('class', 'examples');

        },

        update_feeling_groups: function() {

            var group_bind = this.chart.selectAll("g.timeline-group")
                .data(this.collection.models);

            //Do enter and exit
            this.feeling_group_enter(group_bind.enter());
            var group_exit = group_bind.exit()
                .remove();


            //Now update
            var self = this;
            var lines = group_bind.select('path.line')
                .style("stroke", function(g) {
                    return self.color(g.get('word'));
                })
                .transition()
                .duration(this.transition_duration())
                .attr("d", function(g) {
                    return self.line(g.get('recent_series').slice(skip_window_size));
                })
                .style('opacity', function(d) {
                    if (d.is_selected() || !d.collection.selected_group) {
                        return 1;
                    } else {
                        return 0.15
                    }
                });
        }
    });

})(window);