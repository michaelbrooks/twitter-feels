(function() {
    var logger = Logger.get("thermometer");

    var ThermometerApp = window.apps.thermometer.ThermometerApp = function () {

    };

    ThermometerApp.prototype.start = function() {

        var data = window.thermometer_data;

        //Apply successive moving averages
        var window_sizes = [7, 5, 3];
//        var window_sizes = [5];

        var table = $('.timeline.table');
        var header = $('<thead>').appendTo(table);

        var headerRow = $('<tr>').appendTo(header);
        headerRow.append('<th>');
        data.recent.frames.forEach(function(frame, i) {
            if (i > window_sizes[0]) {
                headerRow.append('<th>' + i + '</th>');
            }
        });

        var body = $('<tbody>').appendTo(table);
        data.feelings.forEach(function(feeling, i) {

            var normal = data.normal.feeling_percents[i];

            var row = $('<tr>').appendTo(body);
            row.append('<td>' + feeling.word + '</td>');

            window_sizes.forEach(function(window_size) {
                var queue = [];
                var current_sum = undefined;

                data.recent.frames.forEach(function(frame, j) {
                    var percent = frame.feeling_percents[i]
                    if (current_sum === undefined) {
                        current_sum = percent;
                    }

                    queue.push(percent);
                    current_sum += percent;

                    if (queue.length > window_size) {
                        var first = queue.shift();
                        current_sum -= first;
                    }

                    if (j > window_size) {
                        frame.feeling_percents[i] = current_sum / queue.length;
                    }
                });
            });

            data.recent.frames.forEach(function(frame, j) {
                if (j > window_sizes[0]) {
                    var diff = (frame.feeling_percents[i] - normal) / normal;
                    diff = (100 * diff).toFixed(1);
                    row.append('<td>' + diff + '%</td>');
                }
            });

        });

    };

    //Get started
    $(document).ready(function () {
        var thermometer = new ThermometerApp();
        thermometer.start();
    });

    logger.info("ThermometerApp loaded");

})();