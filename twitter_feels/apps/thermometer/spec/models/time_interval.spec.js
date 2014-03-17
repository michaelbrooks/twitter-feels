/**
 * Tests for thermometer/models/time_interval.js
 *
 * Created by mjbrooks on 3/15/14.
 */
(function (win) {

    describe('thermometer/models/time_interval.js', function() {

        var therm = win.namespace.get('thermometer');
        var models = win.namespace.get('thermometer.models');

        it('attaches to the thermometer.models namespace', function() {
            expect(models.TimeInterval).toBeDefined();
        });

        it('sets default attributes', function() {

            var interval = new models.TimeInterval();

            expect(interval.get('start')).toBeDefined();
            expect(interval.get('end')).toBeDefined();
            expect(interval.get('duration')).toBeDefined();

            expect(interval.get('asdfasdfasdf')).not.toBeDefined();
        });

        it('parses raw json attributes', function() {

            var end = new Date();
            var duration = 1434; //seconds
            var start = new Date(end.getTime() - duration * 1000);

            var utils = therm.utils;

            //This is the json structure expected
            var attributes = {
                duration: duration,
                start: utils.date_format(start),
                end: utils.date_format(end)
            };

            var interval = new models.TimeInterval(attributes, { parse: true });

            expect(interval.get('start')).toEqual(start);
            expect(interval.get('end')).toEqual(end);
            expect(interval.get('duration')).toEqual(duration);
        });

        it('can calculate the final start_time in this interval', function() {
            var end = new Date();
            var duration = 1434; //seconds
            var start = new Date(end.getTime() - duration * 1000);
            var frame_width = 45;
            var final_start_time = new Date(end.getTime() - frame_width * 1000);

            var utils = therm.utils;

            //This is the json structure expected
            var attributes = {
                duration: duration,
                start: utils.date_format(start),
                end: utils.date_format(end),
                frame_width: frame_width
            };

            var interval = new models.TimeInterval(attributes, { parse: true });

            expect(interval.get_last_start_time()).toEqual(final_start_time);
        });

    });

})(window);