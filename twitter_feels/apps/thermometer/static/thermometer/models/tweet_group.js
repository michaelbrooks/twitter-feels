/**
 * Created by mjbrooks on 3/14/14.
 */
(function (win) {

    var models = win.namespace.get('thermometer.models');
    var utils = win.namespace.get('thermometer.utils');

    var libs = win.namespace.get('libs');

    //For the moving average
    var window_sizes = [9];

    models.TweetGroup = libs.Backbone.Model.extend({

        idAttribute: "feeling_id",

        defaults: function () {
            return {
                recent_series: [],
                examples: []
            };
        },

        parse: function (raw) {

            //Tasks:
            // Compute percent change
            // Convert to Date
            // Calculate a smoothed value
            // If there are examples, copy the smoothed percent change onto them
            var normal = raw.normal;

            if (raw.recent_series.length &&
                _.has(raw.recent_series[0], 'percent')) {

                var percent_smoothed = undefined;
                _.each(window_sizes, function(window_size) {
                    if (percent_smoothed) {
                        percent_smoothed = utils.moving_average(window_size, percent_smoothed);
                    } else {
                        percent_smoothed = utils.moving_average(window_size, raw.recent_series, function(d) {
                            return d.percent;
                        });
                    }
                });
            }

            _.each(raw.recent_series, function (point, i) {
                point.start_time = utils.date_parse(point.start_time);

                if ('percent' in point) {
                    point.percent_change = (point.percent - normal) / normal;
                    point.percent_smoothed = percent_smoothed[i];
                    point.percent_change_smoothed = (point.percent_smoothed - normal) / normal;
                }
            });

            if (raw.examples) {
                var point_index = _.indexBy(raw.recent_series, 'frame_id');
                _.each(raw.examples, function(example) {
                    var point = point_index[example.frame_id];
                    example.percent_change_smoothed = point.percent_change_smoothed;
                    example.start_time = point.start_time;
                    example.word = raw.word;
                });
            }

            return raw;
        },

        toggle_selected: function() {
            if (this.collection) {
                if (this.is_selected()) {
                    this.collection.selected_group = undefined
                } else {
                    if (this.collection.selected_group) {
                        var old_selection = this.collection.selected_group;
                        this.collection.selected_group = this;
                        old_selection.trigger('change');
                    } else {
                        this.collection.selected_group = this;
                    }
                }
                this.trigger('change');
            }
        },

        is_selected: function() {
            if (this.collection) {
                return this.collection.selected_group == this;
            }
            return false;
        }
    });

    models.TweetGroupCollection = libs.Backbone.Collection.extend({
        model: models.TweetGroup,

        set: function() {
            //Call through to parent
            libs.Backbone.Collection.prototype.set.apply(this, arguments);
            //Just send one change event
            this.trigger('change');
        }
    });

})(window);