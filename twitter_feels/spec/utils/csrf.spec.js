/**
 * Tests for assets/twitter_feels/jquery_csrf.js
 *
 * Created by mjbrooks on 3/15/14.
 */
(function (win) {

    describe("twitter_feels/utils/jquery_csrf.js", function () {

        //Not needed here
        //jasmine.getFixtures().fixturesPath = '__spec__/spec/fixtures';

        var utils = win.namespace.get('twitter_feels.utils');


        it('should attach to the utils namespace', function () {
            expect(utils.csrf).toBeDefined();
        });

        it("should not find the csrf token when there is not one", function () {
            var result = utils.csrf.get_csrf();
            expect(result).toEqual(undefined);
        });

        it("should find the csrf token in the DOM", function () {

            var token = 'asdf4125341298357';
            setFixtures('<div id="csrf-token" data-csrf="' + token + '"></div>');

            expect(utils.csrf.get_csrf()).toEqual(token);

        });

        it("should add beforeSend to $.ajaxSetup", function () {

            spyOn($, 'ajaxSetup');

            utils.csrf.jquery_install();

            expect($.ajaxSetup).toHaveBeenCalledWith(jasmine.any(Object));

            var ajaxSetupParams = $.ajaxSetup.calls.first().args[0];
            expect(ajaxSetupParams.beforeSend).toEqual(jasmine.any(Function));

        });

        it("should insert csrf header before ajax POST", function () {

            var token = 'asdf1239458175294';

            spyOn(utils.csrf, 'get_csrf').and.returnValue(token);
            spyOn($, 'ajaxSetup');

            utils.csrf.jquery_install();
            var ajaxSetupParams = $.ajaxSetup.calls.first().args[0];

            var xhr = jasmine.createSpyObj('xhr', ['setRequestHeader']);
            var settings = { type: 'POST' };

            ajaxSetupParams.beforeSend(xhr, settings);

            expect(xhr.setRequestHeader).toHaveBeenCalledWith("X-CSRFToken", token);
        });

        it("should not insert csrf header before ajax GET", function() {
            var token = 'asdf1239458175294';

            spyOn(utils.csrf, 'get_csrf').and.returnValue(token);
            spyOn($, 'ajaxSetup');

            utils.csrf.jquery_install();
            var ajaxSetupParams = $.ajaxSetup.calls.first().args[0];

            var xhr = jasmine.createSpyObj('xhr', ['setRequestHeader']);
            var settings = { type: 'GET' };

            ajaxSetupParams.beforeSend(xhr, settings);

            expect(xhr.setRequestHeader).not.toHaveBeenCalled();
        })
    });

})(window);