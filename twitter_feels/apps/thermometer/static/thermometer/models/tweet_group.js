/**
 * Created by mjbrooks on 3/14/14.
 */
(function (win) {

    var models = win.namespace.get('thermometer.models');
    var utils = win.namespace.get('thermometer.utils');

    var libs = win.namespace.get('libs');

    models.TweetGroup = libs.Backbone.Model.extend({

        idAttribute: "feeling_id",

        defaults: function () {
            return {
                recent_series: []
            };
        },

        parse: function (raw) {
            _.each(raw.recent_series, function (point) {
                point.start_time = utils.date_parse(point.start_time);
            });

            return raw;
        }
    });

    models.TweetGroupCollection = libs.Backbone.Collection.extend({
        model: models.TweetGroup
    });

})(window);