/**
 * Sets up a global 'preload' object with get/set functions
 * for storing initial data directly from templates.
 */
(function (win) {

    var utils = win.namespace.get('twitter_feels.utils');

    utils.Config = function () {
        var _store = {};

        /**
         * Store the value by key.
         *
         * @param key
         * @param value
         */
        this.set = function (key, value) {
            _store[key] = value;
        };

        /**
         * Retrieve data by key, with optional default.
         * Throws an error if the key is not set and there is no default.
         *
         * @param key
         * @param [defaultVal]
         * @returns {*}
         */
        this.get = function (key, defaultVal) {
            if (this.contains(key)) {
                return _store[key]
            }

            if (typeof defaultVal === 'undefined') {
                throw key + " is not set and no default was provided."
            }
            return defaultVal || undefined;
        };

        /**
         * Returns true if the store contains the given key.
         *
         * @param key
         * @returns {boolean}
         */
        this.contains = function (key) {
            return key in _store;
        };
    };

})(window);