var barchartData;

//http://learnjsdata.com/read_data.html
d3.csv("decadeStats.csv", function (data) {
    barchartData = data;

    var w = 200;
    var h = 250;

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
            //return i * (w / barchartData.length);
            return 0;
        })
        .attr("y", function (d, i) {
            //return 50;
            return (i * (h / barchartData.length)) + 10;
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
            //return i * (w / barchartData.length);
            return 30;
        })
        .attr("y", function (d, i) {
            //return h - d.AbilitiesCount * 1;
            return i * (h / barchartData.length);
        })
        //.attr("width", w / barchartData.length - barPadding)
        /*.attr("height", function (d) {
            return d.AbilitiesCount * 1;
        })*/
        .attr("width", function (d) {
            return d.AbilitiesCount * 1;
        })
        .attr("height", h / barchartData.length - barPadding)
        .on("click", function (d, i) {
            //toggleVisibilityPerDecade(d.Decade);
            renderNetworkGraph(d.Decade + ".json");
        });
}); // END d3.csv
