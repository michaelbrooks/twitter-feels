/**
 * Created by mjbrooks on 3/14/14.
 */
(function (ns, $, _, Backbone) {

    var m = ns.models;
    var logger = ns.logger;

    /**
     * Given an even namespace, returns
     * an event handler that will re-trigger the event on 'this',
     * but within the given namespace.
     *
     * @param ns
     * @returns {Function}
     */
    var proxy = function(ns) {
        return function(name) {

            var args = Array.prototype.slice.call(arguments);
            args[0] = ns + ':' + name;

            this.trigger.apply(this, args);
        }
    };

    // The data package which we update over time
    m.UpdateModel = function () {

        this.intervals = {
            normal: new m.TimeInterval(),
            historical: new m.TimeInterval(),
            recent: new m.TimeInterval()
        };

        this.overall = new m.TweetGroup();
        this.selected_feelings = new m.TweetGroupCollection([]);

        this.listenTo(this.intervals.normal, 'all', proxy('intervals:normal'));
        this.listenTo(this.intervals.historical, 'all', proxy('intervals:historical'));
        this.listenTo(this.intervals.recent, 'all', proxy('intervals:recent'));
        this.listenTo(this.overall, 'all', proxy('overall'));
        this.listenTo(this.selected_feelings, 'all', proxy('selected_feelings'));
    };

    _.extend(m.UpdateModel.prototype, Backbone.Events, {

        /**
         * Apply an update to this model based on raw data.
         *
         * @param raw
         */
        apply_update: function (raw) {

            //Update all the time intervals
            _.each(this.intervals, function (rawInterval, name, intervals) {
                intervals[name].set(rawInterval, { parse: true });
            });

            //Update the overall tweet group
            this.overall.set(raw.overall, { parse: true });

            //Update the collection of feelings tweets
            this.selected_feelings.set(raw.selected_feelings, { parse: true });
        },

        /**
         * Requests new data from the server and updates the model
         * if the data has changed.
         *
         * Returns a promise object -- when done, this
         */
        fetch: function () {
            var self = this;

            return $.get(ns.app.urls.update)
                .done(function (response) {
                    self.apply_update(response);
                })
                .fail(function (err) {
                    logger.error('Failed to update data', err);
                });
        }

    });


})(window.apps.thermometer, jQuery, _, Backbone);