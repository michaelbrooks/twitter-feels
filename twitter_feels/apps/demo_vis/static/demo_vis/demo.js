(function () {

    //Use this nice logger
    var logger = Logger.get("demo_vis");

    /**
     * Renders the data using jQuery
     *
     * @param data
     */
    var render_data = function (data) {

        var tbody = $('.vis tbody');

        //Remove all the existing rows
        tbody.html('');

        data.forEach(function (entry, i) {
            var time = new Date(1000 * entry[0]);
            var count = entry[1];

            var row = $('<tr>').appendTo(tbody);
            row.append('<td>' + time.toLocaleTimeString() + '</td>');
            row.append('<td>' + count + '</td>');
        });
    };

    /**
     * Renders the data using D3
     */
    var render_data_d3 = function (data) {

        var tbody = d3.select('.vis tbody');

        var bind = tbody.selectAll('tr').data(data);

        //Make new rows for new data
        var new_rows = bind.enter().append('tr');
        new_rows.append('td')
            .attr('class', 'time');
        new_rows.append('td')
            .attr('class', 'count');

        //Remove unused rows
        bind.exit().remove();

        //Update row data
        bind.select('td.time')
            .text(function(d, i) {
                var time = new Date(1000 * d[0]);
                return time.toLocaleTimeString();
            });
        bind.select('td.count')
            .text(function(d, i) {
                return d[1];
            });
    };

    var get_new_data = function () {
        logger.debug("Requesting data...");

        $.get('/demo_vis/data.json')
            .done(function (result) {
                logger.debug("New data acquired");
                render_data_d3(result);
            })
            .fail(function (err) {
                logger.error("Failed to get data");
            });
    };

    $(document).ready(function () {

        // Get new data every 15 seconds
        setInterval(get_new_data, 15000);
        // And right away as well
        get_new_data();

        logger.info("DemoVis started");
    });

    logger.info("DemoVis loaded");

})(/* DON'T FORGET THESE PARENS! */);