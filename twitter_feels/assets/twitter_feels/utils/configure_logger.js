/**
 * Created by mjbrooks on 3/14/14.
 */
(function (win, Logger) {

    var utils = win.namespace.get('twitter_feels.utils');
    var libs = win.namespace.get('libs');

    /**
     * Configure the Logger class.
     * The level should be Logger.DEBUG, Logger.INFO, Logger.WARN, Logger.ERROR, or Logger.OFF
     *
     * @param [defaultLevel]
     */
    utils.configure_logger = function(defaultLevel) {

        var Logger = libs.Logger;

        if (!Logger) {
            throw "No logger to configure";
        }

        Logger.setLevel(defaultLevel || Logger.DEBUG);

        // Check for the presence of a logger.
        if (!("console" in win) || !(win.console)) {

            //Use 'log'
            Logger.setHandler(function(messages, context) {
                // Prepend the logger's name to the log message for easy identification.
                if (context.name) {
                    messages[0] = (new Date()).toLocaleTimeString() + " [" + context.name + "] " + messages[0];
                }

                win.log.apply(this, messages);
            });

        } else {

            //Use window.console
            Logger.setHandler(function(messages, context) {
                var console = win.console;
                var hdlr = console.log;

                // Prepend the logger's name to the log message for easy identification.
                if (context.name) {
                    messages[0] = (new Date()).toLocaleTimeString() + " [" + context.name + "] " + messages[0];
                }

                // Delegate through to custom warn/error loggers if present on the console.
                if (context.level === Logger.WARN && console.warn) {
                    hdlr = console.warn;
                } else if (context.level === Logger.ERROR && console.error) {
                    hdlr = console.error;
                } else if (context.level === Logger.INFO && console.info) {
                    hdlr = console.info;
                }

                hdlr.apply(console, messages);
            });
        }
    };
})(window);