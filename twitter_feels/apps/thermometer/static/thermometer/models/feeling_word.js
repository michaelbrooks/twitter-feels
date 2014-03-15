/**
 * Created by mjbrooks on 3/14/14.
 */
(function (win) {

    var therm = win.namespace.get('thermometer');
    var models = win.namespace.get('thermometer.models');
    var libs = win.namespace.get('libs');

    /**
     * Represents an individual feeling word.
     *
     * @type {*|void}
     */
    models.FeelingWord = libs.Backbone.Model.extend({

        is_hidden: function () {
            return this.get('hidden');
        }

    });

    /**
     * Collection of feeling words.
     *
     * @type {*|void}
     */
    models.FeelingWordCollection = libs.Backbone.Collection.extend({
        model: models.FeelingWord,
        url: function() {
            return therm.app.urls.feelings;
        }
    });

})(window);