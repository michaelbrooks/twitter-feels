/**
 * Created by mjbrooks on 3/14/14.
 */
(function (win) {

    var models = win.namespace.get('thermometer.models');
    var utils = win.namespace.get('thermometer.utils');
    var libs = win.namespace.get('libs');

    /**
     * Represents a time interval.
     *
     * @type {*|void}
     */
    models.TimeInterval = libs.Backbone.Model.extend({

        defaults: function () {
            var now = new Date();
            return {
                start: now,
                end: now,
                duration: 0
            };
        },

        parse: function (raw) {
            return {
                start: utils.date_parse(raw.start),
                end: utils.date_parse(raw.end),
                duration: raw.duration
            };
        }
    });

})(window);