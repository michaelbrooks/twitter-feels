/**
 * Tests for thermometer/utils.js
 *
 * Created by mjbrooks on 3/15/14.
 */
(function (win) {

    describe('thermometer/utils.js', function() {

        var utils = win.namespace.get('thermometer.utils');

        it('attaches to the thermometer.utils namespace', function() {
            expect(utils.date_format).toBeDefined();
            expect(utils.proxy).toBeDefined();
        });

        it('formats and parses dates consistently', function() {
            var d = new Date();

            var formatted = utils.date_format(d);
            var parsed = utils.date_parse(formatted);

            expect(parsed).toEqual(d);
        });

        it('proxies namespaced events', function() {

            var eventable = jasmine.createSpyObj('eventable', ['trigger']);
            var event_namespace = 'ns';
            var event_name = 'event';
            var handler = utils.proxy(event_namespace);

            //If we call handler with the 'eventable' object as its context,
            //then we should expect trigger to get called on eventable with the
            //namespaced event we give to the handler.
            handler.call(eventable, event_name, 1, 2, 3);

            expect(eventable.trigger).toHaveBeenCalledWith(event_namespace + ':' + event_name, 1, 2, 3);
        });

        it('computes moving averages', function() {

            expect(utils.moving_average(2, [2, 4])).toEqual([2, 3]);
            expect(utils.moving_average(2, [2, 4, 6])).toEqual([2, 3, 5]);
            expect(utils.moving_average(3, [3, 5, 1])).toEqual([3, 4, 3]);

        });

        it('computes moving averages over objects', function() {
            var series = [3, 5, 1];
            series = _.map(series, function(v) {
                return {
                    key: v
                };
            });

            var result = utils.moving_average(3, series, function(d) { return d.key });

            expect(result).toEqual([3, 4, 3]);
        });

        it('calculates unique percents', function() {

            var percents = [0, 0, 0];
            expect(utils.unique_percents(percents)).toEqual([0]);

            percents = [0, 0.5, 1];
            expect(utils.unique_percents(percents)).toEqual(percents);

            percents = [0.1, 0.11, 0.09];
            expect(utils.unique_percents(percents)).toEqual(percents);

            percents = [0.1, 0.101];
            expect(utils.unique_percents(percents)).toEqual([0.1]);

            percents = [0.09, 0.091, 0.099, 0.1];
            expect(utils.unique_percents(percents)).toEqual([0.09, 0.1]);
        });
    });

})(window);