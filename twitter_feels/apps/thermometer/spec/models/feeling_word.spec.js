/**
 * Tests for thermometer/models/feeling_word.js
 *
 * Created by mjbrooks on 3/15/14.
 */
(function (win) {

    describe('thermometer/models/feeling_word.js', function() {

        var models = win.namespace.get('thermometer.models');

        it('attaches to the thermometer.models namespace', function() {
            expect(models.FeelingWord).toBeDefined();
            expect(models.FeelingWordCollection).toBeDefined();
        });

    });

})(window);