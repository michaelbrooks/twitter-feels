(function () {

    console.log("status loaded");

    //Milliseconds between status checks
    var POLLING_INTERVAL = 15000;

    var get_refresh_button = function() {
        return $('#refresh-status');
    }

    var get_thermometer_status = function () {
        return $('#thermometer-status');
    };

    var get_thermometer_toggle = function () {
        return $('#thermometer-toggle');
    };

    var get_streamer_status = function() {
        return $('#streamer-status')
    };

    var get_status_url = function () {
        return $('#urls').data('status-url');
    };

    var get_start_url = function () {
        return get_thermometer_toggle().data('start-url');
    };

    var get_stop_url = function () {
        return get_thermometer_toggle().data('stop-url');
    };

    /**
     * Updates the thermometer toggle button with a new state.
     *
     * The state can either be true, false, or undefined.
     *
     * @param state
     */
    var update_toggle = function (state) {
        var toggle = get_thermometer_toggle();

        if (!toggle) return;

        toggle.bootstrapSwitch('disabled', state === undefined);
        if (state !== undefined) {
            toggle.bootstrapSwitch('state', state)
        }
    };

    /**
     * Displays the status on the indicator.
     *
     * Provide no response if the status could not be obtained.
     *
     * @param [response]
     */
    var display_thermometer_status = function (thermometerStatus) {
        var indicator = get_thermometer_status();

        if (thermometerStatus) {
            indicator.replaceWith(thermometerStatus.html);
            update_toggle(thermometerStatus.running);
        } else {
            indicator.text("Unknown");
            indicator.removeClass('label-success label-warning')
            indicator.addClass('label-danger');
            update_toggle(undefined);
        }
    };

    /**
     * Display updated streamer status.
     *
     * @param [streamerStatus]
     */
    var display_streamer_status = function(streamerStatus) {
        if (streamerStatus) {
            var indicator = get_streamer_status();
            indicator.html(streamerStatus.html);
        }
    };

    /**
     * Checks the status.
     */
    var update_status = function () {
        get_refresh_button().prop('disabled', true);

        var url = get_status_url();
        $.get(url)
            .done(function (response) {
                display_thermometer_status(response.thermometer);
                display_streamer_status(response.streamer);
            })
            .fail(function (err) {
                console.log("Failed to obtain status.", err);
                display_thermometer_status(undefined);
                display_streamer_status(undefined);
            })
            .always(function() {
                schedule_next_poll();
                get_refresh_button().prop('disabled', false);
            });
    };

    /**
     * Set a timeout for the next status update.
     */
    var schedule_next_poll = function () {
        //Do it again in 30 seconds
        setTimeout(update_status, POLLING_INTERVAL);
    };

    /**
     * The toggle has changed value. Tell the server
     * and then update the display.
     * @param toggle
     * @param value
     */
    var toggle_changed = function (toggle, value) {
        var url = value ? get_start_url() : get_stop_url();

        //Disable the toggle for now
        update_toggle(undefined);

        $.post(url)
            .done(function (response) {
                display_thermometer_status(response);
            })
            .fail(function (err) {
                console.log("Failed to update thermometer.", err);
                display_thermometer_status(undefined);
            });
    };

    $(document).ready(function () {

        //Start polling for status
        schedule_next_poll();

        //Set up the toggle button
        var toggle = get_thermometer_toggle();
        if (toggle) {
            //Activate the toggle
            toggle.bootstrapSwitch();

            //Listen for toggle changes
            toggle.on('switchChange', function (e, data) {
                toggle_changed(toggle, data.value);
            });
        }

        get_refresh_button().click(function() {
            update_status();
        });

    });

})();