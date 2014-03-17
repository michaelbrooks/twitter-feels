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

    /**
     * Returns a list of feeling IDs from the URL.
     *
     * @returns {Array}
     */
    utils.feelings_from_url = function() {
        return [1, 2, 3];
    };

    /**
     * Updates the url with a list of feelings
     *
     * @param feelings
     */
    utils.feelings_to_url = function(feelings) {

    };

    /**
     * Calculates a simple moving average of the given series, with the given window size.
     * Returns the smoothed series.
     *
     * @param window_size
     * @param series
     * @param [accessor]
     * @returns {Array}
     */
    utils.moving_average = function(window_size, series, accessor) {

        if (window_size < 2) {
            throw "Window size of " + window_size + " makes no sense";
        }

        var window = [],
            window_sum = 0,
            val = undefined,
            first = undefined;

        var result = [];

        for (var i = 0; i < series.length; i++) {
            if (accessor) {
                val = accessor(series[i], i);
            } else {
                val = series[i];
            }

            window_sum += val;
            window.push(val);

            if (window.length > window_size) {
                first = window.shift();
                window_sum -= first;
            }

            result.push(window_sum / window.length);
        }

        return result;
    };

    /**
     * Given a list of percentages (0.0 - 1.0),
     * returns the subset that are unique when rounded to 0 decimal points.
     *
     * @param values
     * @returns {*}
     */
    utils.unique_percents = function(values) {
        return _.uniq(_.map(values, function(v) {
            return Math.round(100.0 * v) / 100.0;
        }));
    }

})(window);