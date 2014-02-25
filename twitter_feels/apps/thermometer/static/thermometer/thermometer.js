(function() {
    var logger = Logger.get("thermometer");

    var ThermometerApp = window.apps.thermometer.ThermometerApp = function () {

    };

    ThermometerApp.prototype.start = function() {
        var data = window.thermometer_data;
        var table = $('.timeline.table');
        var header = $('<thead>').appendTo(table);

        var headerRow = $('<tr>').appendTo(header);
        headerRow.append('<th>');
        data.frames.data.forEach(function(frame, i) {
            headerRow.append('<th>' + i + '</th>');
        });

        var body = $('<tbody>').appendTo(table);
        data.feelings.forEach(function(feeling, i) {

            var normal = data.normal.feeling_counts[i];

            var row = $('<tr>').appendTo(body);
            row.append('<td>' + feeling.word + '</td>');

            data.frames.data.forEach(function(frame, j) {
                var count = frame.feeling_counts[i];
                var diff = (count - normal) / normal
                row.append('<td>' + 100 * diff + '</td>');
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