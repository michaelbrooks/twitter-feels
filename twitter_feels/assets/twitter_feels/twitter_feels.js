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

    var initializers = [];
    tf.TwitterFeels.add_initializer = function(callback) {
        initializers.push(callback);
    };

    tf.TwitterFeels.initialize = function(options) {
        options = _.defaults(
            options || {},
            win._twitter_feels_config || {},
            default_options);

        if (options.debug && libs.Logger) {
            utils.configure_logger(libs.Logger.DEBUG);
        } else {
            utils.configure_logger(libs.Logger.WARN);
        }

        if (options.csrf) {
            utils.csrf.jquery_install();
        }

        tf.app = new tf.TwitterFeels(options);

        //Initialize all the other stuff
        _.each(initializers, function(callback) {
            callback();
        })
    };

})(window);