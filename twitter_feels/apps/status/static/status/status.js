(function () {

    var logger = Logger.get("status");

    //Milliseconds between status checks
    var POLLING_INTERVAL = 15000;

    var StatusApp = window.apps.status.StatusApp = function () {

        this.ui = {
            refresh_button: $('#refresh-status'),
            task_table: $('table.tasks')
        };

        if (this.ui.refresh_button) {
            this.init_refresh();
        }

        this.task_views = {};
        this.init_task_views();
    };

    StatusApp.prototype.start = function() {
        if (this.status_url) {
            logger.info("polling every " + (POLLING_INTERVAL / 1000) + " seconds");
            //Start polling for status
            this.schedule_next_poll();
        }

        logger.info("StatusApp started");
    };

    /**
     * Listen for refresh button clicks.
     */
    StatusApp.prototype.init_refresh = function() {
        var self = this;
        this.status_url = this.ui.refresh_button.data('status-url');

        this.ui.refresh_button.click(function () {
            self.update_status();
        });
    };

    /**
     * Initialize a TaskView for every task in the table.
     */
    StatusApp.prototype.init_task_views = function () {
        var self = this;
        this.ui.task_table.find('tr.task-row').each(function () {
            var row = $(this),
                key = row.data('task-key');
            self.task_views[key] = new window.apps.status.TaskView(row);
        });
    };

    /**
     * Checks the status of all tasks.
     */
    StatusApp.prototype.update_status = function () {
        var self = this;
        this.ui.refresh_button.prop('disabled', true);

        logger.debug("Querying task status.");

        $.get(self.status_url)
            .done(function (response) {

                $.each(response, function (key, status) {
                    self.display_status(key, status);
                });
                //display_streamer_status(response.streamer);
            })
            .fail(function (err) {
                logger.error("Failed to obtain status.", err);
                self.display_status();
//                display_streamer_status(undefined);
            })
            .always(function () {
                self.schedule_next_poll();
                self.ui.refresh_button.prop('disabled', false);
            });
    };

    /**
     * Displays the updated status for a particular task (by key).
     *
     * If key/status are undefined, assumes failure to reach server.
     *
     * @param [key]
     * @param [status]
     */
    StatusApp.prototype.display_status = function (key, status) {
        if (key) {
            var task_view = this.task_views[key];
            task_view.display_status(status);
        } else {
            $.each(this.task_views, function (key, task_view) {
                task_view.display_status(status);
            });
        }
    };

    /**
     * Set a timeout for the next status update.
     */
    StatusApp.prototype.schedule_next_poll = function () {
        var self = this;
        setTimeout(function () {
            self.update_status()
        }, POLLING_INTERVAL);
    };


    var get_streamer_status = function () {
        return $('#streamer-status')
    };

    /**
     * Display updated streamer status.
     *
     * @param [streamerStatus]
     */
    var display_streamer_status = function (streamerStatus) {
        if (streamerStatus) {
            var indicator = get_streamer_status();
            indicator.html(streamerStatus.html);
        }
    };

    //Get started
    $(document).ready(function () {
        var status = new StatusApp();
        status.start();
    });

    logger.info("StatusApp loaded");

})();