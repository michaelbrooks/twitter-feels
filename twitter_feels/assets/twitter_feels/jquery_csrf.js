/**
 * Configure jQuery to pass Django's CSRF token with ajax requests.
 *
 * You must modify your <body> element to include the csrf token:
 *
 * <body data-url="{{ csrf_token }}">
 *  ...
 * </body>
 */
(function () {
    // Generate a token
    var csrf = $('body').data('csrf');

    /// Necessary to set the CSRF token for ajax requests.
    /// https://docs.djangoproject.com/en/dev/ref/contrib/csrf/
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrf);
            }
        }
    });
})();
