/**
 * Tests for thermometer/models/update.js
 *
 * Created by mjbrooks on 3/15/14.
 */
(function (win) {

    describe('thermometer/models/update.js', function () {

        var models = win.namespace.get('thermometer.models');
        var utils = win.namespace.get('thermometer.utils');

        it('attaches to the thermometer.models namespace', function () {
            expect(models.UpdateModel).toBeDefined();
        });

        it('provides an event api', function () {

            var instance = new models.UpdateModel();

            expect(instance.on).toEqual(jasmine.any(Function));
            expect(instance.trigger).toEqual(jasmine.any(Function));
        });

        it('initializes with default data', function () {

            var instance = new models.UpdateModel();

            expect(instance.intervals).toEqual(jasmine.any(Object));
            expect(instance.intervals.normal).toEqual(jasmine.any(models.TimeInterval));

            expect(instance.overall).toEqual(jasmine.any(models.TweetGroup));
            expect(instance.selected_feelings).toEqual(jasmine.any(models.TweetGroupCollection));
        });

        it('proxies events from its child data structures', function () {

            var instance = new models.UpdateModel();

            var spy = jasmine.createSpyObj('eventSpies', ['overall', 'intervals', 'selected_feelings']);
            instance.on('overall:change', spy.overall);
            instance.on('intervals:historical:change', spy.intervals);
            instance.on('selected_feelings:change', spy.selected_feelings);

            instance.overall.trigger('change', 23);
            instance.intervals.historical.trigger('change', 353);
            instance.selected_feelings.trigger('change', 378, 3432);

            expect(spy.overall).toHaveBeenCalledWith(23);
            expect(spy.intervals).toHaveBeenCalledWith(353);
            expect(spy.selected_feelings).toHaveBeenCalledWith(378, 3432);
        });

        it('updates its child data structures', function () {

            var instance = new models.UpdateModel();

            var raw = {
                intervals: {
                    normal: "normal",
                    historical: "historical",
                    recent: "recent"
                },
                overall: "overall",
                selected_feelings: [
                    "feeling 1",
                    "feeling 2"
                ]
            };

            spyOn(instance.overall, 'set');
            spyOn(instance.selected_feelings, 'set');

            spyOn(instance.intervals.normal, 'set');
            spyOn(instance.intervals.historical, 'set');
            spyOn(instance.intervals.recent, 'set');

            //Somebody had better call parse on those time intervals
            //We'll just return the name of the time interval from our input data
            spyOn(models.TimeInterval.prototype, 'parse').and.callFake(function(rawInterval) {
                var match = undefined;
                _.each(raw.intervals, function(input, intervalName) {
                    if (input == rawInterval) {
                        match = intervalName;
                    }
                });
                return match;
            });

            instance.apply_update(raw);

            expect(instance.overall.set).toHaveBeenCalledWith(raw.overall, { parse: true });
            expect(instance.selected_feelings.set).toHaveBeenCalledWith(raw.selected_feelings, { parse: true });

            // interval.set(interval.parse(raw.intervals[name]));

            expect(models.TimeInterval.prototype.parse).toHaveBeenCalledWith(raw.intervals.normal);
            expect(models.TimeInterval.prototype.parse).toHaveBeenCalledWith(raw.intervals.historical);
            expect(models.TimeInterval.prototype.parse).toHaveBeenCalledWith(raw.intervals.recent);

            expect(instance.intervals.normal.set).toHaveBeenCalledWith('normal');
            expect(instance.intervals.historical.set).toHaveBeenCalledWith('historical');
            expect(instance.intervals.recent.set).toHaveBeenCalledWith('recent');

        });

    });

})(window);