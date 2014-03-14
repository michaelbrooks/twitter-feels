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

    var date_format = function(d) {
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

        parse: function (raw) {
            _.each(raw.display_series, function (point) {
                point.start_time = date_parse(point.start_time);
            });

            return raw;
        }
    });

    var TweetGroupCollection = Backbone.Collection.extend({
        model: TweetGroup
    });


    var request_update = function () {

        var request = $.get(urls.update);

        //Filter the request results to construct the appropriate models
        return request.then(
            function (response) {

                //Turn all the intervals into TimeIntervals
                _.each(response.intervals, function (rawInterval, name, intervals) {
                    intervals[name] = new TimeInterval(rawInterval, { parse: true });
                });

                //Data about totals
                response.overall = new TweetGroup(response.overall, { parse: true });

                //Data about feelings
                response.selected_feelings = new TweetGroupCollection(response.selected_feelings, {parse: true});

                return response;
            },
            function (err) {
                logger.error('Failed to request update data', err);
            }
        );
    };

    thermometer.models = {
        FeelingWord: FeelingWord,
        FeelingWordCollection: FeelingWordCollection,
        TimeInterval: TimeInterval,
        request_update: request_update
    };

})();