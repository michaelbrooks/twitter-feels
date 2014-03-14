(function() {
    var margin = {top: 20, right: 80, bottom: 30, left: 50},
        width = 800 - margin.left - margin.right,
        height = 200 - margin.top - margin.bottom;

    var x = d3.time.scale()
        .range([0, width]);

    var y = d3.scale.linear()
        .range([height, 0]);

    var color = d3.scale.category10();

    var xAxis = d3.svg.axis()
        .scale(x)
        .orient("bottom");

    var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left");

    var svg = d3.select("body").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis)
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text("Temperature (ºF)");

    return function(groups, xAccessor, yAccessor, groupLabelAccessor, groupSeriesAccessor) {

        var line = d3.svg.line()
            .interpolate("basis")
            .x(function(d) { return x(xAccessor(d)); })
            .y(function(d) { return y(yAccessor(d)); });

        color.domain(groups.map(groupLabelAccessor));

        x.domain(d3.extent(groupSeriesAccessor(groups[0]), xAccessor(d)));

        y.domain([
            d3.min(groups, function(g) { return d3.min(groupSeriesAccessor(g), yAccessor); }),
            d3.max(groups, function(g) { return d3.max(groupSeriesAccessor(g), yAccessor); })
        ]);

        var group = svg.selectAll(".timeline-group")
            .data(groups)
            .enter().append("g")
            .attr("class", "timeline-group");

        group.append("path")
            .attr("class", "line")
            .attr("d", groupSeriesAccessor)
            .style("stroke", function(d) { return color(groupLabelAccesor(d)); });

        group.append("text")
            .datum(function(d) { return {name: d.name, value: d.values[d.values.length - 1]}; })
            .attr("transform", function(d) { return "translate(" + x(d.value.date) + "," + y(d.value.temperature) + ")"; })
            .attr("x", 3)
            .attr("dy", ".35em")
            .text(function(d) { return d.name; });
    }

})();