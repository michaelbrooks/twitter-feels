/**
 * Created by mjbrooks on 3/14/14.
 */
(function (win) {

    var therm = win.namespace.get('thermometer');
    var models = win.namespace.get('thermometer.models');
    var utils = win.namespace.get('thermometer.utils');
    var libs = win.namespace.get('libs');

    var logger = libs.Logger.get('thermometer.models.update');

    // The data package which we update over time
    models.UpdateModel = function () {

        this.intervals = {
            normal: new models.TimeInterval(),
            historical: new models.TimeInterval(),
            recent: new models.TimeInterval()
        };

        this.overall = new models.TweetGroup();
        this.selected_feelings = new models.TweetGroupCollection([]);

        this.proxy_events();
    };

    _.extend(models.UpdateModel.prototype, libs.Backbone.Events, {

        proxy_events: function() {
            this.listenTo(this.intervals.normal, 'all', utils.proxy('intervals:normal'));
            this.listenTo(this.intervals.historical, 'all', utils.proxy('intervals:historical'));
            this.listenTo(this.intervals.recent, 'all', utils.proxy('intervals:recent'));
            this.listenTo(this.overall, 'all', utils.proxy('overall'));
            this.listenTo(this.selected_feelings, 'all', utils.proxy('selected_feelings'));
        },

        /**
         * Apply an update to this model based on raw data.
         *
         * @param raw
         */
        apply_update: function (raw) {

            //Update all the time intervals
            _.each(this.intervals, function (interval, name) {
                if (_.has(raw.intervals, name)) {
                    interval.set(raw.intervals[name], { parse: true });
                }
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

            return $.get(therm.app.urls.update)
                .done(function (response) {
                    self.apply_update(response);
                })
                .fail(function (err) {
                    logger.error('Failed to update data', err);
                });
        }

    });


})(window);