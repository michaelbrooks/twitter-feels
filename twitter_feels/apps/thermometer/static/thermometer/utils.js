/**
 * Created by mjbrooks on 3/14/14.
 */
(function (win) {

    var utils = win.namespace.get('thermometer.utils');

    /**
     * Convert a date into a json date string
     * @param d
     * @returns {number}
     */
    utils.date_format = function (d) {
        return d.getTime();
    };

    /**
     * Convert a json date string into a Date
     * @param str
     * @returns {Date}
     */
    utils.date_parse = function (str) {
        return new Date(str);
    };


    /**
     * Given an even namespace, returns
     * an event handler that will re-trigger the event on 'this',
     * but within the given namespace.
     *
     * @param ns
     * @returns {Function}
     */
    utils.proxy = function (ns) {
        return function (name) {

            var args = Array.prototype.slice.call(arguments);
            args[0] = ns + ':' + name;

            this.trigger.apply(this, args);
        }
    };

})(window);