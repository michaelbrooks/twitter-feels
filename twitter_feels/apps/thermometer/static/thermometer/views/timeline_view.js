/**
 * View for showing timelines.
 *
 * Created by mjbrooks on 3/15/14.
 */
(function (win) {

    var views = win.namespace.get('thermometer.views');
    var utils = win.namespace.get('thermometer.utils');
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
        tooltip_template: _.template($('#tweet-tooltip-template').html()),

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

            var self = this;
            this.tip = d3.tip()
                .offset([-10, 0])
                .attr('class', 'd3-tip')
                .html(function(d) {
                    d.time_ago = utils.time_ago(d.created_at);
                    return self.tooltip_template(d);
                });

            $(document)
                .on('click.thermometer.timeline', '.d3-tip', function(e) {
                    e.stopPropagation();
                })
                .on('click.thermometer.timeline', function(e) {
                    //Don't do anything on circles, let d3 handle it
                    if ($(e.target).is('.examples circle')) {
                        return;
                    }

                    if (self.selected_circle) {
                        self.hide_tip();
                    }
                });

            this.svg.call(this.tip);
        },

        remove: function() {
            $(document).off('click.thermometer.timeline');
            this.hide_tip();
            return views.CommonView.prototype.remove.apply(this, arguments);
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
                .attr('class', 'examples fade');

        },

        example_enter: function(enter) {
            var self = this;

            enter.append('circle')
                .attr('r', 10)
                .on("click", function(d) {
                    var already_selected = d3.event.target === self.selected_circle;

                    if (already_selected) {
                        self.hide_tip();
                    } else {
                        self.show_tip(d3.event.target, d);
                    }
                });
        },

        show_tip: function(circle, data) {
            if (this.selected_circle) {
                this.hide_tip();
            }

            this.selected_circle = circle;
            data = data || circle.__data__;

            d3.select(this.selected_circle).classed('selected', true);
            this.tip.show(data);
        },

        hide_tip: function() {
            if (!this.selected_circle) {
                return;
            }

            d3.select(this.selected_circle).classed('selected', false);
            this.selected_circle = undefined;
            this.tip.hide();
        },

        update_feeling_groups: function() {

            var group_bind = this.chart.selectAll("g.timeline-group")
                .data(this.collection.models);

            //Do enter and exit
            this.feeling_group_enter(group_bind.enter());

            group_bind.exit()
                .remove();

            //Now update
            var self = this;

            group_bind.classed('selected', function(g) {
                    return g.is_selected();
                });

            var lines = group_bind.select('path.line')
                .style("stroke", function(g) {
                    return self.color(g.get('word'));
                })
                .transition()
                .duration(this.transition_duration())
                .attr("d", function(g) {
                    return self.line(g.get('recent_series').slice(skip_window_size));
                })
                .style('opacity', function(g) {
                    if (g.is_selected() || !g.collection.selected_group) {
                        return 1;
                    } else {
                        return 0.15
                    }
                });

            var example_group = group_bind.select('g.examples');

            var example_bind = example_group.selectAll('circle')
                .data(function(g) {
                    return g.get('examples');
                });

            this.example_enter(example_bind.enter());

            example_bind.exit()
                .remove();

            example_bind
                .transition()
                .duration(this.transition_duration())
                .attr('cx', function(d) {
                    return self.xScale(d.start_time);
                })
                .attr('cy', function(d) {
                    return self.yScale(d.percent_change_smoothed);
                })
                .style("stroke", function(d) {
                    return self.color(d.word);
                })
                .style("fill", function(d) {
                    return self.color(d.word);
                });

            example_group
                .classed('in', function(g) {
                    return g.is_selected();
                });
        }
    });

})(window);