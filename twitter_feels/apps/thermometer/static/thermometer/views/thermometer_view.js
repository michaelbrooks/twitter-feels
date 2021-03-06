/**
 * View for showing thermometers.
 *
 * Created by mjbrooks on 3/15/14.
 */
(function (win) {

    var views = win.namespace.get('thermometer.views');
    var utils = win.namespace.get('thermometer.utils');
    var libs = win.namespace.get('libs');

    var d3 = libs.d3;
    var logger = libs.Logger.get('thermometer.views.thermometer_view');

    var recent_window = 3;
    var dimensions = {
        total_width: 100,
        total_height: 320
    };

    var TUBE_RADIUS = 3;
    var TUBE_BUFFER_TOP = 14;

    dimensions.middle_x = dimensions.total_width * 0.5;
    dimensions.bulb_y = dimensions.total_height - dimensions.total_width * 0.5;
    dimensions.bulb_x = dimensions.middle_x
    dimensions.bulb_radius = dimensions.total_width * 0.14;
    dimensions.tube_width = dimensions.total_width * 0.13;
    dimensions.tube_height = dimensions.bulb_y - dimensions.tube_width;
    dimensions.tube_radius = dimensions.tube_width * 0.5;
    dimensions.tube_x = dimensions.middle_x - dimensions.tube_width * 0.5;
    dimensions.tube_y = dimensions.tube_width;
    dimensions.bulb_top = dimensions.bulb_y - dimensions.bulb_radius;

    var yScale = d3.scale.linear()
        .range([dimensions.bulb_radius, dimensions.tube_height])
        .domain([0, 0.1]);

    views.ThermometerView = views.CommonView.extend({

        className: 'thermometer-view fade',

        template: _.template($('#thermometer-view-template').html()),

        ui: {
            svg: 'svg',
            fill: '.tube.fill',
            tube: '.tube.back',
            bulb: '.bulb.fill',
            feeling: '.label',
            normal: '.normal-indicator',
            historical: '.historical-indicator',
            label_group: '.label-group',
            minus: '.minus'
        },

        events: {
            'click': 'clicked'
        },

        initialize: function(options) {
            //Expects the model to be a TweetGroup with a feeling
            this.color = options.color || "red";

            this.percent = d3.format(".0%");

            this.has_rendered = false;
            this.listenTo(this.model, 'change', this.render);

            logger.debug('initialized', options);
        },

        set_color: function(color) {
            if (this.color != color) {
                this.color = color;
                this.render();
            }
        },

        clicked: function() {
            this.model.toggle_selected();
        },

        /**
         * Prepare the packet of data needed by d3
         */
        get_data: function() {
            var historical = this.model.get('historical');
            var normal = this.model.get('normal');

            var series = this.model.get('recent_series');
            var recent_percent = d3.mean(series.slice(series.length - recent_window), function(d) {
                return d.percent;
            });

            return {
                feeling_id: this.model.get('feeling_id'),
                recent: recent_percent,
                historical: historical,
                normal: normal,
                word: this.model.get('word')
            }
        },

        render: function() {

            var data = this.get_data();

            if (!this.has_rendered) {
                logger.debug('running template...');

                //Make some skeleton HTMl with an underscore template
                this.$el.html(this.template(data));

                this.bindUIElements();

                this.ui.minus.tooltip({
                    placement: 'top'
                });

                this.has_rendered = true;
            }

            var color = this.color || '#' + this.model.get('color');
            this.ui.bulb.css('background', color);
            this.ui.fill.css('background', color);

            this.$el.toggleClass('selected', this.model.is_selected());

            var percents = utils.unique_percents([data.normal, data.historical, data.recent]);

            var label_bind = d3.select(this.ui.label_group[0])
                .selectAll('div')
                .data(percents);

            label_bind.enter()
                .append('div');

            label_bind.exit()
                .remove();

            //Delay the final rendering to make sure the elements are in the document
            var self = this;
            setTimeout(function() {
                //Get the actual current dimensions of the bulb and the tube
                var bulb_radius = self.ui.bulb.height() * 0.5;
                var tube_height = self.ui.tube.height();
                yScale.range([bulb_radius, tube_height - TUBE_BUFFER_TOP]);

                var duration = 1500;

                var norm = d3.select(self.ui.normal[0]);
                var hist = d3.select(self.ui.historical[0]);

                //Animate the fill
                d3.select(self.ui.fill[0])
                    .transition()
                    .duration(duration)
                    .style('height', yScale(data.recent) + TUBE_RADIUS + "px")
//                    .each('end', function() {
//                        norm.transition()
//                            .duration(duration)
//                            .style('opacity', 1);
//
//                        hist.transition()
//                            .duration(duration)
//                            .style('opacity', 1);
//                    });

                norm.classed('in', true);
                hist.classed('in', true);

                label_bind.text(self.percent);

                if (self.has_rendered_data) {
                    //Animate if we've rendered before
                    norm = norm.transition()
                        .duration(duration);
                    hist = hist.transition()
                        .duration(duration);

                    label_bind = label_bind.transition()
                        .duration(duration)
                }

                norm.style('bottom', yScale(data.normal) + bulb_radius + "px");
                hist.style('bottom', yScale(data.historical) + bulb_radius + "px");
                label_bind.style('bottom', function(v) {
                    return (yScale(v) + bulb_radius) + "px";
                });

                self.has_rendered_data = true;

                //Fade it in
                utils.fade(self.$el, true);

                logger.debug('rendered');
            }, 1);

            return this;
        },

        show_norm_hist: function() {

        },

        render_svg: function(data) {

            //Then do the d3 bind/enter/exit/update thing
            var svg = d3.select(this.ui.svg[0])
                .attr('width', dimensions.total_width)
                .attr('height', dimensions.total_height);

            var bind = svg.selectAll('g.glyph').data([data]);

            var newGlyph = bind.enter().append('g').attr('class', 'glyph');

            newGlyph.append('rect')
                .attr('width', dimensions.tube_width)
                .attr('height', dimensions.tube_height)
                .attr('x', dimensions.tube_x)
                .attr('y', dimensions.tube_y)
                .attr('rx', dimensions.tube_radius)
                .attr('ry', dimensions.tube_radius);

            newGlyph.append('rect')
                .attr('class', 'indicator')
                .attr('width', dimensions.tube_width)
                .attr('height', dimensions.tube_height - yScale(0) + dimensions.bulb_radius)
                .attr('x', dimensions.tube_x)
                .attr('y', yScale(0))
                .attr('rx', dimensions.tube_radius)
                .attr('ry', dimensions.tube_radius)
                .attr('fill', this.color);

            newGlyph.append('circle')
                .attr('cx', dimensions.bulb_x)
                .attr('cy', dimensions.bulb_y)
                .attr('r', dimensions.bulb_radius);

            //Update things
            bind.select('rect.indicator')
                .transition()
                .attr('y', function(d) {
                    return yScale(d.recent);
                })
                .attr('height', function(d) {
                    return dimensions.tube_height - yScale(d.recent) + dimensions.bulb_radius;
                })
                .attr('fill', this.color);

            bind.select('circle.bulb')
                .attr('fill', this.color);
        }
    });

})(window);