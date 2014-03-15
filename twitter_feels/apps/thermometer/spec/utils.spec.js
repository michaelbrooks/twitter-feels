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

    });

})(window);