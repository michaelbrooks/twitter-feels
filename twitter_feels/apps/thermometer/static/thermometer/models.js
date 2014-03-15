/**
 * Model classes for Thermometer JS app
 */
(function () {
    var thermometer = window.apps.thermometer;
    var preload = window.preload;
    var logger = Logger.get("thermometer.models");

    var debug_date_parse = preload.get('debug');

    var urls = {
        feelings: preload.get('thermometer.urls.feelings'),
        update: preload.get('thermometer.urls.update')
    };

    var date_format = function (d) {
        return d.getTime();
    };

    var date_parse = function (str) {
        var d = new Date(str);

        if (debug_date_parse && (date_format(d) !== str)) {
            throw ("Date parse failed for " + str)
        }

        return d
    };

    /**
     * Represents an individual feeling word.
     *
     * @type {*|void}
     */
    var FeelingWord = Backbone.Model.extend({

        is_hidden: function () {
            return this.get('hidden');
        }

    });

    /**
     * Collection of feeling words.
     *
     * @type {*|void}
     */
    var FeelingWordCollection = Backbone.Collection.extend({
        model: FeelingWord,
        url: urls.feelings
    });

    /**
     * Represents a time interval.
     *
     * @type {*|void}
     */
    var TimeInterval = Backbone.Model.extend({

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
                start: date_parse(raw.start),
                end: date_parse(raw.end),
                duration: raw.duration
            };
        }
    });

    var TweetGroup = Backbone.Model.extend({

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
                point.start_time = date_parse(point.start_time);
            });

            return raw;
        }
    });

    var TweetGroupCollection = Backbone.Collection.extend({
        model: TweetGroup
    });

    // The data package which we update over time
    var UpdateModel = function () {

        this.intervals = {
            normal: new TimeInterval(),
            historical: new TimeInterval(),
            recent: new TimeInterval()
        };

        this.overall = new TweetGroup();
        this.selected_feelings = new TweetGroupCollection([]);

        var proxy = function(ns) {
            return function(name) {

                var args = Array.prototype.slice.call(arguments);
                args[0] = ns + ':' + name;

                this.trigger.apply(this, args);
            }
        };

        this.listenTo(this.intervals.normal, 'all', proxy('intervals:normal'));
        this.listenTo(this.intervals.historical, 'all', proxy('intervals:historical'));
        this.listenTo(this.intervals.recent, 'all', proxy('intervals:recent'));
        this.listenTo(this.overall, 'all', proxy('overall'));
        this.listenTo(this.selected_feelings, 'all', proxy('selected_feelings'));
    };

    _.extend(Backbone.Events, {

        /**
         * Apply an update to this model based on raw data.
         *
         * @param raw
         */
        apply_update: function (raw) {

            //Update all the time intervals
            _.each(raw.intervals, function (rawInterval, name, intervals) {
                intervals[name].set(rawInterval, { parse: true });
            });

            //Update the overall tweet group
            raw.overall.set(raw.overall, { parse: true });

            //Update the collection of feelings tweets
            raw.selected_feelings.set(raw.selected_feelings, { parse: true });
        },

        /**
         * Requests new data from the server and updates the model
         * if the data has changed.
         *
         * Returns a promise object -- when done, this
         */
        fetch: function () {
            var self = this;

            return $.get(urls.update)
                .done(function (response) {
                    self.apply_update(response);
                })
                .fail(function (err) {
                    logger.error('Failed to update data', err);
                });
        }

    });

    thermometer.models = {
        FeelingWordCollection: FeelingWordCollection,
        UpdateModel: UpdateModel
    };

})();