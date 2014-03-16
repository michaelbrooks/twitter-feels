(function (win) {

    var st = win.namespace.get('status');
    var libs = win.namespace.get('libs');

    var logger = libs.Logger.get("status");

    //Milliseconds between status checks
    var POLLING_INTERVAL = 15000;

    var StatusApp = st.StatusApp = function () {

        this.ui = {
            refresh_button: $('#refresh-status'),
            task_table: $('table.tasks'),
            streamer_status: $('#streamer-status'),
            workers_status: $('#workers-status'),
            queues_status: $('#queues-status'),
            general_status: $('#general-status'),
            _clean_tweets_button: function() { return $('.clean-tweets') },
            _requeue_failed_button: function() { return $('.requeue-failed') }
        };

        if (this.ui.refresh_button) {
            this.init_refresh();
        }

        if (this.ui._clean_tweets_button()) {
            this.init_clean_tweets();
        }

        if (this.ui._requeue_failed_button()) {
            this.init_requeue_failed();
        }

        this.task_views = {};
        this.init_task_views();
    };

    StatusApp.prototype.start = function () {
        if (this.status_url) {

            logger.info("Polling every " + (POLLING_INTERVAL / 1000) + " seconds");

            //Start polling for status
            this.schedule_next_poll();
        }

        this.updates_paused = false;

        logger.info("StatusApp started");
    };

    /**
     * Listen for refresh button clicks.
     */
    StatusApp.prototype.init_refresh = function () {
        var self = this;
        this.status_url = this.ui.refresh_button.data('status-url');

        this.ui.refresh_button.click(function () {
            if (self.updates_paused) return;

            self.update_status();
        });
    };

    /**
     * Disable or enable status updates and actions. One thing at a time.
     */
    StatusApp.prototype.pause_updates = function(updates_paused) {
        this.updates_paused = updates_paused;

        var clean_button = this.ui._clean_tweets_button()
        if (clean_button) {
            clean_button.prop('disabled', updates_paused);
        }

        if (this.ui.refresh_button) {
            this.ui.refresh_button.prop('disabled', updates_paused);
        }

        if (updates_paused) {
            logger.debug("Updates paused");
        } else {
            logger.debug("Updates resumed");
        }
    };

    /**
     * Set up handler for clean tweets button.
     */
    StatusApp.prototype.init_clean_tweets = function () {
        var self = this;

        this.ui.streamer_status.on('click', '.clean-tweets', function () {
            if (self.updates_paused) return;
            
            self.clean_tweets();
        });
    };

    /**
     * Set up handler for requeue failed jobs button.
     */
    StatusApp.prototype.init_requeue_failed = function () {
        var self = this;

        this.ui.queues_status.on('click', '.requeue-failed', function () {
            if (self.updates_paused) return;

            self.requeue_failed();
        });
    };

    /**
     * Send a request to clean unneeded tweets.
     */
    StatusApp.prototype.clean_tweets = function() {
        var self = this;
        logger.debug("Removing analyzed tweets.");

        var clean_url = this.ui._clean_tweets_button().data('clean-url');

        this.pause_updates(true);

        $.post(clean_url)
            .done(function (response) {
                logger.debug("Analyzed tweets successfully removed.");
                self.display_status_block(self.ui.streamer_status, response);
            })
            .fail(function (err) {
                logger.error("Failed to remove analyzed tweets.", err);
                self.display_status_block(self.ui.streamer_status, undefined);
            })
            .always(function () {
                self.pause_updates(false);
            });
    };

    /**
     * Send a request to requeue failed jobs.
     */
    StatusApp.prototype.requeue_failed = function() {
        var self = this;
        logger.debug("Requeuing failed jobs.");

        var requeue_url = this.ui._requeue_failed_button().data('requeue-url');

        this.pause_updates(true);

        $.post(requeue_url)
            .done(function (response) {
                logger.debug("Failed jobs successfully requeued.");
                self.display_status_block(self.ui.queues_status, response);
            })
            .fail(function (err) {
                logger.error("Failed to requeue jobs.", err);
                self.display_status_block(self.ui.queues_status, undefined);
            })
            .always(function () {
                self.pause_updates(false);
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
            self.task_views[key] = new st.TaskView(row);
        });
    };

    /**
     * Checks the status of all tasks.
     */
    StatusApp.prototype.update_status = function (schedule_next) {
        var self = this;

        this.pause_updates(true);

        logger.debug("Querying task status.");

        $.get(self.status_url)
            .done(function (response) {

                $.each(response.tasks, function (key, status) {
                    self.display_task_status(key, status);
                });

                self.display_status_block(self.ui.streamer_status, response.streamer);
                self.display_status_block(self.ui.queues_status, response.queues);
                self.display_status_block(self.ui.workers_status, response.workers);
                self.display_status_block(self.ui.general_status, response.general);
            })
            .fail(function (err) {
                logger.error("Failed to obtain status.", err);
                self.display_task_status();
                self.display_status_block(self.ui.streamer_status, undefined);
                self.display_status_block(self.ui.queues_status, undefined);
                self.display_status_block(self.ui.workers_status, undefined);
                self.display_status_block(self.ui.general_status, undefined);
            })
            .always(function () {
                if (schedule_next) {
                    self.schedule_next_poll();
                }
                self.pause_updates(false)
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
    StatusApp.prototype.display_task_status = function (key, status) {
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
     * Display updated status for a block replace html element
     *
     * @param element
     * @param newHtml
     */
    StatusApp.prototype.display_status_block = function (element, newHtml) {
        if (newHtml) {
            element.html(newHtml);
        }
    };

    /**
     * Set a timeout for the next status update.
     */
    StatusApp.prototype.schedule_next_poll = function () {
        var self = this;
        setTimeout(function () {

            if (self.updates_paused) {
                self.schedule_next_poll();
            } else {
                self.update_status(true)
            }

        }, POLLING_INTERVAL);
    };

    //Get started
    $(document).ready(function () {
        var status = new StatusApp();
        status.start();
    });

    logger.info("StatusApp loaded");

})(window);