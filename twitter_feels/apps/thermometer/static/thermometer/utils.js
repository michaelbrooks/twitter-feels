/**
 * Created by mjbrooks on 3/14/14.
 */
(function (ns, tf) {

    ns.utils = {

        date_format: function (d) {
            return d.getTime();
        },

        date_parse: function (str) {
            var d = new Date(str);

            if (tf.app.debug && (this.date_format(d) !== str)) {
                throw ("Date parse failed for " + str)
            }

            return d
        }
    };

})(window.apps.thermometer, window.apps.twitter_feels);