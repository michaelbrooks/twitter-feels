/**
 * Model classes for Thermometer JS app
 */
(function () {
    var thermometer = window.apps.thermometer;
    var preload = window.preload;
    var logger = Logger.get("thermometer.models");

    var urls = {
        feelings: preload.get('thermometer.urls.feelings'),
        update: preload.get('thermometer.urls.update')
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
                start: new Date(raw.start),
                end: new Date(raw.end),
                duration: raw.duration
            };
        }
    });

    var TweetGroup = Backbone.Model.extend({
        parse: function (raw) {
            return {
//                start: new Date(raw.start),
//                end: new Date(raw.end),
//                duration: raw.duration
            };
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

                response.selected_feelings = _.map(response.selected_feelings, function(rawGroup, i, list) {
                    return
                });

                console.log(response);

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