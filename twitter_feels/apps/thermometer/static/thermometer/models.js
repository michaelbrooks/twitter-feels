/**
 * Model classes for Thermometer JS app
 */
(function () {
    var thermometer = window.apps.thermometer;
    var preload = window.preload;

    var urls = {
        feelings: preload.get('thermometer.urls.feelings'),
        update: preload.get('thermometer.urls.update')
    };

    var Feeling = Backbone.Model.extend({

        is_hidden: function() {
            return this.get('hidden');
        }

    });

    var FeelingsCollection = Backbone.Collection.extend({
        model: Feeling,
        url: urls.feelings
    });

    thermometer.models = {
        Feeling: Feeling,
        FeelingsCollection: FeelingsCollection
    };

})();