/**
 * Configure jQuery to pass Django's CSRF token with ajax requests.
 *
 * You must modify your <body> element to include the csrf token:
 *
 * <body data-url="{{ csrf_token }}">
 *  ...
 * </body>
 */
(function (win, $) {

    var utils = win.namespace.get('twitter_feels.utils');

    /// Necessary to set the CSRF token for ajax requests.
    /// https://docs.djangoproject.com/en/dev/ref/contrib/csrf/
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    utils.csrf = {

        selector: '#csrf-token',

        get_csrf: function() {
            return $(utils.csrf.selector).data('csrf');
        },

        jquery_install: function() {
            $.ajaxSetup({

                crossDomain: false, // obviates need for sameOrigin test

                beforeSend: function (xhr, settings) {

                    var csrf = utils.csrf.get_csrf();

                    if (!csrfSafeMethod(settings.type)) {
                        xhr.setRequestHeader("X-CSRFToken", csrf);
                    }
                }
            });
        }
    };

})(window, jQuery);
