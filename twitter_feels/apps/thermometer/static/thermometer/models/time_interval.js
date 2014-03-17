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
                duration: 0,
                frame_width: 60
            };
        },

        parse: function (raw) {
            raw.start = utils.date_parse(raw.start);
            raw.end = utils.date_parse(raw.end);
            return raw;
        },

        /**
         * Return the latest start_time expected in this interval.
         *
         * @returns {Date}
         */
        get_last_start_time: function() {
            return new Date(this.get('end') - this.get('frame_width') * 1000);
        }
    });

})(window);