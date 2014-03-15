/**
 * Initialize the twitter_feels common infrastructure.
 */
(function (ns, Logger) {

    ns.utils = {};

    ns.TwitterFeels = function(options) {
        this.debug = options.debug;
    };


    var default_options = {
        debug: false,
        csrf: true
    };

    ns.initialize = function(options) {
        _.defaults(options, default_options);

        if (options.debug) {
            ns.utils.configure_logger(Logger.DEBUG);
        } else {
            ns.utils.configure_logger(Logger.WARN);
        }

        if (options.csrf) {
            ns.utils.csrf.jquery_install();
        }

        ns.app = new ns.TwitterFeels(options);
    };

})(window.apps.twitter_feels, Logger);