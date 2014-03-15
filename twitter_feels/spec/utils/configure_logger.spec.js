/**
 * Tests for twitter_feels/utils/configure_logger.js
 *
 * Created by mjbrooks on 3/15/14.
 */
(function (win) {

    describe("twitter_feels/utils/configure_logger.js", function () {

        var utils = win.namespace.get('twitter_feels.utils');
        var libs = win.namespace.get('libs');

        var Logger, console;

        beforeEach(function() {
            Logger = libs.Logger;
            delete libs.Logger;

            console = win.console;
            win.console = undefined;
        });

        afterEach(function() {
            libs.Logger = Logger;
            win.console = console;
        });

        it("it should attach to the utils namespace", function () {
            expect(utils.configure_logger).toBeDefined();
        });

        it("should fail if the Logger library is not available", function() {
            expect(utils.configure_logger).toThrow();
        });

        it("should set the default Logger level", function() {

        });

        it("should allow setting the Logger level", function() {

        });

        it("should set the Logger handler", function() {

            //Restore the Logger so it works properly
            libs.Logger = Logger;

            spyOn(Logger, 'setHandler');

            utils.configure_logger();

            //Should have tried to set the log handler
            expect(Logger.setHandler).toHaveBeenCalledWith(jasmine.any(Function));
        });

        it("should use window.log if window.console is not available", function() {

            //Restore the Logger so it works properly
            libs.Logger = Logger;

            spyOn(Logger, 'setHandler');
            utils.configure_logger();

            //Here's the handler it set
            var handler = Logger.setHandler.calls.first().args[0];

            //We'll call the handler with these arguments
            var message = "hello";
            var context = { name: 'ERROR' };

            spyOn(win, 'log');
            handler([message], context);

            //It should call window.log
            expect(win.log).toHaveBeenCalledWith(jasmine.any(String));

            //It should pass along messages (possibly modified) containing our message
            var printed = window.log.calls.first().args[0];
            expect(printed.indexOf(message)).toBeGreaterThan(-1);
        });

        it("should use window.console if available", function() {
            //Restore the logger and console
            libs.Logger = Logger;
            //We'll use a fake console that only supports 'log'
            win.console = jasmine.createSpyObj('console', ['log']);

            spyOn(Logger, 'setHandler');
            utils.configure_logger();

            //Here's the handler it set
            var handler = Logger.setHandler.calls.first().args[0];

            //We'll call the handler with these arguments
            var message = "hello";
            var context = { name: 'ERROR' };

            handler([message], context);

            //It should call window.log
            expect(win.console.log).toHaveBeenCalledWith(jasmine.any(String));

            //It should pass along a message containing our message
            var printed = win.console.log.calls.first().args[0];
            expect(printed.indexOf(message)).toBeGreaterThan(-1);
        })
    });

})(window);