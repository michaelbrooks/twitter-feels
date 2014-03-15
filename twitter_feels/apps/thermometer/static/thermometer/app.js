/**
 * Created by mjbrooks on 3/14/14.
 */
(function (win) {

    var therm = win.namespace('thermometer');
    var models = win.namespace('thermometer.models');
    var libs = win.namespace('libs');

    var logger;

    // The thermometer app class
    therm.Thermometer = function(options) {

        this.urls = options.urls;

        this.feelings = new models.FeelingWordCollection(options.init_feelings);
    };

    var default_options = {
        urls: {
            feelings: '/feelings',
            update: '/update'
        },
        init_feelings: []
    };

    // A static init function
    therm.Thermometer.initialize = function(options) {
        _.defaults(options, default_options);

        logger =  libs.Logger.get('thermometer');

        //Create a global instance of the app
        therm.app = new therm.Thermometer(options);
    };

})(window);