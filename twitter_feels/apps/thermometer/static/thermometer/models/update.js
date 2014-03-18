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
    models.UpdateModel = function (options) {

        this.feelings_list = options.feelings_list;

        //A good guess about recent interval we're going to get from the server
        var recent_end = new Date();
        recent_end.setMinutes(recent_end.getMinutes() - 1, 0, 0);
        var duration = 60 * 60;
        var recent_start = new Date(recent_end.getTime() - duration * 1000);

        this.intervals = {
            normal: new models.TimeInterval(),
            historical: new models.TimeInterval(),
            recent: new models.TimeInterval({
                duration: duration,
                start: recent_start,
                end: recent_end
            })
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
                    interval.set(interval.parse(raw.intervals[name]));
                }
            });

            //Update the overall tweet group
            this.overall.set(raw.overall, { parse: true });

            //Update the collection of feelings tweets
            this.selected_feelings.set(raw.selected_feelings, { parse: true });

            var self = this;
            self.feelings_list.each(function(feeling) {
                var not_contains = !self.selected_feelings.get(feeling.id)
                feeling.set('selected', !not_contains);
            });
        },

        /**
         * Requests new data from the server and updates the model
         * if the data has changed.
         *
         * Returns a promise object -- when done, this
         */
        fetch: function (feeling_ids) {
            var self = this;

            feeling_ids = feeling_ids || this.get_selected_feelings() || [];

            this.fetching = feeling_ids;

            var urlpart = feeling_ids.join(',');

            logger.debug('Fetching updated data for feelings', feeling_ids);
            return $.get(therm.app.urls.update, {
                'feelings': urlpart
            })
                .done(function (response) {
                    if (self.fetching == feeling_ids) {
                        //Only use this data if it is the most recent request
                        self.apply_update(response);
                    } else {
                        logger.debug('Stale update received for feelings', feeling_ids);
                    }
                })
                .fail(function (err) {
                    logger.error('Failed to update data', err);
                })
                .always(function() {
                    self.fetching = false;
                });
        },

        start_fetching: function() {
            var self = this;
            this.interval = setInterval(function() {
                if (!self.fetching) {
                    self.fetch()
                } else {
                    logger.debug('Skipping regular fetch');
                }
            }, 30 * 1000);

            this.fetch();
        },

        /**
         * Returns the currently selected list of feelings.
         *
         * @returns {Array}
         */
        get_selected_feelings: function() {
            return this.selected_feelings.pluck('feeling_id');
        },

        add_feeling: function(feeling_id) {
            var feeling = this.feelings_list.get(feeling_id);
            logger.debug('Adding feeling "' + feeling.get('word') + '"');

            var selected_feeling_ids = this.get_selected_feelings();
            selected_feeling_ids.push(feeling_id);

            this.fetch(selected_feeling_ids);
        },

        remove_feeling: function(feeling_id) {
            var feeling = this.feelings_list.get(feeling_id);

            logger.debug('Removing feeling "' + feeling.get('word') + '"');

            var selected_feeling_ids = this.get_selected_feelings();

            var index = selected_feeling_ids.indexOf(feeling_id);
            selected_feeling_ids.splice(index, 1);

            this.fetch(selected_feeling_ids);
        }

    });


})(window);