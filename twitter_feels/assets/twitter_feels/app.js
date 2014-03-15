/**
 * Initialize the twitter_feels common infrastructure.
 */
(function (win) {

    var tf = win.namespace.get('twitter_feels');
    var utils = win.namespace.get('twitter_feels.utils');
    var libs = win.namespace.get('libs');

    tf.TwitterFeels = function(options) {
        this.debug = options.debug;
    };


    var default_options = {
        debug: false,
        csrf: true
    };

    tf.TwitterFeels.initialize = function(options) {
        _.defaults(options, default_options);

        if (options.debug && libs.Logger) {
            utils.configure_logger(libs.Logger.DEBUG);
        } else {
            utils.configure_logger(libs.Logger.WARN);
        }

        if (options.csrf) {
            utils.csrf.jquery_install();
        }

        tf.app = new tf.TwitterFeels(options);
    };

})(window);