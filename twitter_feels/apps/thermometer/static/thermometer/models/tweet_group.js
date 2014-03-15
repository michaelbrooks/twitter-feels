/**
 * Created by mjbrooks on 3/14/14.
 */
(function (ns) {

    var logger = ns.logger;

    ns.models.TweetGroup = Backbone.Model.extend({

        idAttribute: "feeling_id",

        defaults: function () {
            return {
                recent_series: [],
                word: undefined,
                feeling_id: undefined,
                normal: undefined
            };
        },

        parse: function (raw) {
            _.each(raw.recent_series, function (point) {
                point.start_time = ns.utils.date_parse(point.start_time);
            });

            return raw;
        }
    });

    ns.models.TweetGroupCollection = Backbone.Collection.extend({
        model: ns.models.TweetGroup
    });
})(window.apps.thermometer);