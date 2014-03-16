/**
 * Created by mjbrooks on 3/14/14.
 */
(function (win) {

    var models = win.namespace.get('thermometer.models');
    var utils = win.namespace.get('thermometer.utils');

    var libs = win.namespace.get('libs');

    //For the moving average
    var window_sizes = [7, 5, 3];

    models.TweetGroup = libs.Backbone.Model.extend({

        idAttribute: "feeling_id",

        defaults: function () {
            return {
                recent_series: []
            };
        },

        parse: function (raw) {

            //Tasks:
            // Compute percent change
            // Convert to Date
            // Calculate a smoothed value

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

            return raw;
        }
    });

    models.TweetGroupCollection = libs.Backbone.Collection.extend({
        model: models.TweetGroup,

        initialize: function(options) {

            var self = this;
            this.on('add remove', function() {
                var args = Array.prototype.slice.call(arguments);
                args.unshift('change');
                self.trigger.apply(self, args);
            });
        }
    });

})(window);