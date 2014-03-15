/**
 * Created by mjbrooks on 3/14/14.
 */
(function (ns) {

    //A namespace for thermometer models
    ns.models = {};

    ns.logger = Logger.get('thermometer');

    // The thermometer app class
    ns.Thermometer = function(options) {

        this.urls = options.urls;

        this.feelings = new ns.models.FeelingWordCollection(options.init_feelings);
    };

    var default_options = {
        urls: {
            feelings: '/feelings',
            update: '/update'
        },
        init_feelings: []
    };

    // A static init function
    ns.initialize = function(options) {
        _.defaults(options, default_options);
        ns.app = new ns.Thermometer(options);
    };

})(window.apps.thermometer);