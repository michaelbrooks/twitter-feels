(function() {

    window.apps = {
        status: {},
        thermometer: {}
    };

    //Configure a logger
    window.apps.configureLogger = function(defaultLevel) {

        Logger.setLevel(defaultLevel || Logger.DEBUG);

        // Check for the presence of a logger.
        if (!("console" in window)) {

            //Use 'log'
            Logger.setHandler(function(messages, context) {
                // Prepend the logger's name to the log message for easy identification.
                if (context.name) {
                    messages[0] = (new Date()).toLocaleTimeString() + " [" + context.name + "] " + messages[0];
                }

                log.call(this, messages);
            });
        } else {

            //Use window.console
            Logger.setHandler(function(messages, context) {
                var console = window.console;
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

    Logger.info("apps loaded");
})();