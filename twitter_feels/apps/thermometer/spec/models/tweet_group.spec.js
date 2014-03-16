/**
 * Tests for thermometer/models/tweet_group.js
 *
 * Created by mjbrooks on 3/15/14.
 */
(function (win) {

    describe("thermometer/models/tweet_group.js", function () {

        var utils = win.namespace.get('thermometer.utils');
        var models = win.namespace.get('thermometer.models');

        it('attaches to the thermometer.models namespace', function () {
            expect(models.TweetGroup).toBeDefined();
            expect(models.TweetGroupCollection).toBeDefined();
        });

        it('sets default attributes', function () {

            var group = new models.TweetGroup();

            expect(group.get('recent_series')).toEqual(jasmine.any(Array));
            expect(group.get('word')).toBeUndefined();
            expect(group.get('normal')).toBeUndefined();
            expect(group.get('feeling_id')).toBeUndefined();
        });

        it('parses raw json attributes', function () {

            var recent_series = [];
            var json_recent_series = [];
            for (var i = 0; i < 10; i++) {
                var time = new Date();
                recent_series.push({
                    start_time: time
                });

                json_recent_series.push({
                    start_time: utils.date_format(time)
                });
            }

            var attributes = {
                recent_series: json_recent_series
            };

            var group = new models.TweetGroup(attributes, { parse: true });

            expect(group.get('recent_series')).toEqual(recent_series);
        });

    });

})(window);