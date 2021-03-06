(function (win) {

    var st = win.namespace.get('status');
    var libs = win.namespace.get('libs');

    var logger = libs.Logger.get("status");

    /**
     * A view for task status.
     *
     * @type {TaskView}
     */
    var TaskView = st.TaskView = function (task_row) {
        this.task_row = task_row;
        this.task_key = task_row.data('task-key');

        this.ui = {
            name_cell: task_row.find('td.name-cell'),
            badge_cell: task_row.find('td.badge-cell'),
            most_recent_cell: task_row.find('td.most-recent-cell'),
            avg_analysis_time_cell: task_row.find('td.avg-analysis-time-cell'),
            avg_cleanup_time_cell: task_row.find('td.avg-cleanup-time-cell'),
            frame_count_cell: task_row.find('td.frame-count-cell'),
            switch_cell: task_row.find('td.switch-cell')
        };
        this.ui.badge = this.ui.badge_cell.find('.status-badge');

        if (this.ui.switch_cell) {
            this.init_switch();
        }
    };

    TaskView.prototype.init_switch = function () {
        var self = this;
        this.ui.switch = this.ui.switch_cell.find('input');
        this.start_url = this.ui.switch.data('start-url');
        this.stop_url = this.ui.switch.data('stop-url');

        //Activate the toggle
        this.ui.switch.bootstrapSwitch();
        this.ui.switch_cell.removeClass('invisible');

        //Listen for toggle changes
        this.ui.switch.on('switchChange', function (e, data) {
            self.switch_changed(data.value);
        });
    };


    /**
     * Updates the switch with a new state.
     *
     * The state can either be true, false, or undefined.
     *
     * @param state
     */
    TaskView.prototype.update_switch = function (state) {
        if (!this.ui.switch_cell) return;

        this.ui.switch.bootstrapSwitch('disabled', state === undefined);

        if (state !== undefined) {
            this.ui.switch.bootstrapSwitch('state', state.running)
        }
    };

    /**
     * Update the last time the task was run.
     *
     * @param status
     */
    TaskView.prototype.update_most_recent = function(status) {
        if (!this.ui.most_recent_cell) {
            return;
        }

        if (status) {
            this.ui.most_recent_cell.text(status.most_recent || "None");
        } else {
            this.ui.most_recent_cell.text('?');
        }
    };

    /**
     * Update the total frame count.
     *
     * @param status
     */
    TaskView.prototype.update_frame_count = function(status) {
        if (status) {
            this.ui.frame_count_cell.text(status.frame_count);
        } else {
            this.ui.frame_count_cell.text('?');
        }
    };

    /**
     * Update the average analysis time for this task.
     *
     * @param status
     */
    TaskView.prototype.update_avg_analysis_time = function(status) {
        if (status && status.avg_analysis_time) {
            this.ui.avg_analysis_time_cell.text(status.avg_analysis_time.toFixed(2));
        } else {
            this.ui.avg_analysis_time_cell.text('?');
        }
    };

    /**
     * Update the average cleanup time for this task.
     *
     * @param status
     */
    TaskView.prototype.update_avg_cleanup_time = function(status) {
        if (status && status.avg_cleanup_time) {
            this.ui.avg_cleanup_time_cell.text(status.avg_cleanup_time.toFixed(2));
        } else {
            this.ui.avg_cleanup_time_cell.text('?');
        }
    };

    /**
     * Displays the status on the badge.
     *
     * Provide no response if the status could not be obtained.
     *
     * @param [status]
     */
    TaskView.prototype.display_status = function (status) {

        if (status) {

            logger.debug("Task '" + this.task_key +
                "' is " + (status.running ? "running" : "not running"));

            this.ui.badge_cell.html(status.badge);
            this.ui.badge = this.ui.badge_cell.find('.status-badge');

            this.update_switch(status);
            this.update_most_recent(status);
            this.update_avg_analysis_time(status);
            this.update_avg_cleanup_time(status);
            this.update_frame_count(status);
        } else {

            logger.debug("Status is " + status
                + " on '" + this.task_key + "'");

            this.ui.badge.text("Unknown");
            this.ui.badge.removeClass('label-success label-warning')
            this.ui.badge.addClass('label-danger');
            this.update_switch(undefined);
            this.update_most_recent(undefined);
            this.update_avg_analysis_time(undefined);
            this.update_avg_cleanup_time(undefined);
            this.update_frame_count(undefined);
        }
    };


    /**
     * The toggle has changed value. Tell the server
     * and then update the display.
     *
     * @param value
     */
    TaskView.prototype.switch_changed = function (value) {
        var self = this;
        var url = value ? this.start_url : this.stop_url;

        //Disable the toggle for now
        this.update_switch(undefined);

        logger.debug("Turning " + this.task_key + " " + (value ? "on" : "off"));

        $.post(url)
            .done(function (status) {
                self.display_status(status);
            })
            .fail(function (err) {
                logger.error("Failed to update task.", err);
                self.display_status(undefined);
            });
    };

    logger.info("TaskView loaded");
})(window);