/**
 * Namespace class for managing namespaces by name.
 */
(function (window) {
    "use strict";

    /**
     * Manager for namespaces.
     *
     * @type {Namespace}
     */
    var Namespace = function(top) {
        this.top = top || {};
    };

    /**
     * Retrieve (creating if necessary) a namespace by name.
     *
     * @param name
     */
    Namespace.prototype.get = function(name) {

        var parts = name.split('.');

        //Make sure all the parts exist
        var curr = this.top;

        for (var i = 0; i < parts.length; i++) {

            var segment = parts[i];

            if (segment in curr) {
                curr = curr[segment];
            } else {
                curr = curr[segment] = {};
            }
        }

        return curr;
    };

    // Export to popular environments boilerplate.
    if (typeof define === 'function' && define.amd) {
        define(Namespace);
    }
    else if (typeof module !== 'undefined' && module.exports) {
        module.exports = Namespace;
    }
    else {
        window['Namespace'] = Namespace;
    }

})(window);