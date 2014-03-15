/**
 * Created by mjbrooks on 3/14/14.
 */
(function (ns, Backbone) {

    var logger = ns.logger;

    /**
     * Represents an individual feeling word.
     *
     * @type {*|void}
     */
    ns.models.FeelingWord = Backbone.Model.extend({

        is_hidden: function () {
            return this.get('hidden');
        }

    });

    /**
     * Collection of feeling words.
     *
     * @type {*|void}
     */
    ns.models.FeelingWordCollection = Backbone.Collection.extend({
        model: ns.models.FeelingWord,
        url: function() {
            return ns.app.urls.feelings;
        }
    });

})(window.apps.thermometer, Backbone);