(function() {
    var logger = Logger.get("thermometer");

    var ThermometerApp = window.apps.thermometer.ThermometerApp = function () {

    };

    ThermometerApp.prototype.start = function() {

        var feelings = window.all_feelings;
        var feelings_map = {};
        feelings.forEach(function(feeling, i) {
            feelings_map[feeling.id] = feeling;
        });

        var $app = $('.thermometer-app')
        var $tray = $('.thermometers');
        var render = apps.thermometer.bar_renderer('.thermometers');

        var $timelines = $('.timelines');

        var url = $app.data('data_url');

        var get_recent_percent = function(feeling_data) {
            return feeling_data.recent_percent;
        };

        var get_feeling_label = function(feeling_data) {
            return feelings_map[feeling_data.feeling_id].word;
        };

        $.get(url)
            .done(function(result) {

                var recent_window = 5;
                var selected_feelings = result.selected_feelings;

                selected_feelings.sort(function(a, b) {
                    return b.normal - a.normal;
                });

                //Precalculate recent averages
                selected_feelings.forEach(function(feeling_data) {
                    var recent = 0;
                    for (var i = 1; i <= recent_window; i++) {
                        recent += feeling_data.display_series[feeling_data.display_series.length - i].percent;
                    }
                    feeling_data.recent_percent = recent / 5;
                    console.info(feelings_map[feeling_data.feeling_id], feeling_data.recent_percent);
                });

                render(selected_feelings,
                    get_feeling_label,
                    get_recent_percent
                );
            })
            .fail(function(err) {
                logger.error("Could not get data", err)
            });
    };

    //Get started
    $(document).ready(function () {
        var thermometer = new ThermometerApp();
        thermometer.start();
    });

    logger.info("ThermometerApp loaded");

})();