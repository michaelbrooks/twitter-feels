/**
 * Created by mjbrooks on 3/14/14.
 */
(function (win) {

    var tf = win.namespace.get('twitter_feels');
    var therm = win.namespace.get('thermometer');
    var models = win.namespace.get('thermometer.models');
    var views = win.namespace.get('thermometer.views');

    var libs = win.namespace.get('libs');

    var logger;

    // The thermometer app class
    therm.Thermometer = function(options) {

        this.urls = options.urls;
        this.feelings = new models.FeelingWordCollection(options.init_feelings);
        this.update = new models.UpdateModel();

    };

    therm.Thermometer.prototype.start = function() {

        //Get the major dom elements
        this.layout = new views.ThermometerLayout();

        //Initialize the views
        this.views = {};

        this.views.tray = new views.TrayView({
            collection: this.update.selected_feelings
        });
        this.layout.show('tray', this.views.tray);

        this.views.timelines = new views.TimelineView({
            collection: this.update.selected_feelings
        });
        this.layout.show('timelines', this.views.timelines);

        //Request some data
        this.update.fetch();
    };


    var default_options = {
        urls: {
            feelings: '/feelings',
            update: '/update'
        },
        init_feelings: []
    };

    //Initialize when the main app kicks off
    tf.TwitterFeels.add_initializer(function(options) {
        options = _.defaults(
            options || {},
            win._thermometer_config || {},
            default_options);

        logger =  libs.Logger.get('thermometer');

        //Create a global instance of the app
        therm.app = new therm.Thermometer(options);
        therm.app.start();
    });

})(window);