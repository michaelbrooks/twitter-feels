/**
 * Created by mjbrooks on 3/14/14.
 */
(function (ns, Backbone) {

    var logger = ns.logger;

    /**
     * Represents a time interval.
     *
     * @type {*|void}
     */
    ns.models.TimeInterval = Backbone.Model.extend({

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
                start: ns.utils.date_parse(raw.start),
                end: ns.utils.date_parse(raw.end),
                duration: raw.duration
            };
        }
    });

})(window.apps.thermometer, Backbone);