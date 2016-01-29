var barchartData;

//http://learnjsdata.com/read_data.html
d3.csv("decadeStats.csv", function (data) {
    barchartData = data;

    var w = 500;
    var h = 200;

    var barVis = d3.select("body").select("#barchart")
        .append("svg:svg")
        .attr("width", w)
        .attr("height", h);

    barVis.selectAll("text")
        .data(barchartData)
        .enter()
        .append("text")
        .attr("class", "barlabels")
        .text(function (d) {
            if (d.Decade != 2020)
                return d.Decade;
            else
                return "N/A";
        })
        .attr("x", function (d, i) {
            return i * (w / barchartData.length);
        })
        .attr("y", function (d) {
            return 50;
        });

    var barPadding = 1;
    barVis.selectAll("rect")
        .data(barchartData)
        .enter()
        .append("rect")
        .attr("fill", function (d) {
            return fill(2);
        })
        .attr("opacity", 0.5)
        .attr("x", function (d, i) {
            return i * (w / barchartData.length);
        })
        .attr("y", function (d) {
            return h - d.AbilitiesCount * 1;
        })
        .attr("width", w / barchartData.length - barPadding)
        .attr("height", function (d) {
            return d.AbilitiesCount * 1;
        })
        .on("click", function (d, i) {
            //toggleVisibilityPerDecade(d.Decade);
            renderNetworkGraph(d.Decade + ".json");
        });
}); // END d3.csv
