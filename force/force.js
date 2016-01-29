var w = 1000, //3000,
    h = 800 //3000,
fill = d3.scale.category20();



function renderNetworkGraph(jsonFileName) {
    d3.select("#chart").selectAll("*").remove();

    var vis = d3.select("#chart")
        .append("svg:svg")
        .attr("width", w)
        .attr("height", h);

    d3.json(jsonFileName, function (json) {
        var force = d3.layout.force()
            .charge(-120)
            .linkDistance(30)
            .nodes(json.nodes)
            .links(json.links)
            .size([w, h])
            .start();

        // http://bl.ocks.org/mbostock/3750558 "This example demonstrates how to prevent D3’s force layout from moving nodes that have been repositioned by the user."
        var drag = force.drag()
            .on("dragstart", dragstart);

        function dragstart(d) {
            d3.select(this).classed("fixed", d.fixed = true);
        }

        var link = vis.selectAll("line.link")
            .data(json.links)
            .enter().append("svg:line")
            //.attr("class", "link")
            .attr("class", function (d) {
                return "link " + d.decade;
            })
            .attr("id", function (d) {
                return d.year;
            })
            .style("stroke-width", function (d) {
                return Math.sqrt(d.value);
            })
            .attr("x1", function (d) {
                return d.source.x;
            })
            .attr("y1", function (d) {
                return d.source.y;
            })
            .attr("x2", function (d) {
                return d.target.x;
            })
            .attr("y2", function (d) {
                return d.target.y;
            });

        var g = vis.selectAll("circle.node")
            .data(json.nodes)
            .enter().append("svg:g")
            //.attr("class", "g.nodegroup")
            .attr("class", function (d) {
                return "g.nodegroup " + d.decade;
            })
            .attr("id", function (d) {
                return d.year;
            });

        var node = g.append("svg:circle")
            .attr("class", "node")
            .attr("cx", function (d) {
                return d.x;
            })
            .attr("cy", function (d) {
                return d.y;
            })
            .attr("r", 5)
            .style("fill", function (d) {
                return fill(d.group);
            }) // d referenziert ein JSON-Tag
            .on("click", function (d, i) {
                var pos = d3.mouse(this);
                console.log(pos);
            }) // daz: http://stackoverflow.com/questions/8238990/unable-to-get-click-event-in-d3-javascript-library   http://stackoverflow.com/questions/24394369/adding-onclick-event-to-d3-force-layout-graph
            .call(force.drag);

        var labels = g.append("text")
            //.attr("class", "labels")
            .attr("class", function (d) {
                return "labels " + d.decade;
            })
            .text(function (d) {
                if (d.group == 2) return d.name; // group 2 zeigt Superheldenstatus
            })
            .attr("x", function (d) {
                return d.x;
            })
            .attr("y", function (d) {
                return d.y;
            })
            .call(force.drag);

        var images = g.append("image")
            .attr("xlink:href", function (d) {
                if (d.localFilePath == "N/A") {
                    return "./blank.png";
                } else {
                    return d.localFilePath; // d.picture
                }
                return d.localFilePath;
            })
            .attr("x", function (d) {
                return d.x;
            })
            .attr("y", function (d) {
                return d.y;
            })
            .attr("height", 50)
            .attr("width", 50)
            .call(force.drag);


        //svg:title is automatically interpreted as a mouse-over balloon tip by the browser
        node.append("svg:title")
            .text(function (d) {
                return d.name;
            });

        images.append("svg:title")
            .text(function (d) {
                return d.name;
            });

        vis.style("opacity", 1e-6)
            .transition()
            .duration(1000)
            .style("opacity", 1);

        // muss alle elemente beinhalten, die wichtig sind
        force.on("tick", function () {
            link.attr("x1", function (d) {
                    return d.source.x;
                })
                .attr("y1", function (d) {
                    return d.source.y;
                })
                .attr("x2", function (d) {
                    return d.target.x;
                })
                .attr("y2", function (d) {
                    return d.target.y;
                });


            node.attr("cx", function (d) {
                    return d.x;
                })
                .attr("cy", function (d) {
                    return d.y;
                });

            labels.attr("x", function (d) {
                    return d.x;
                })
                .attr("y", function (d) {
                    return d.y;
                });

            images.attr("x", function (d) {
                    return d.x;
                })
                .attr("y", function (d) {
                    return d.y;
                });
        });
    });
};

renderNetworkGraph("force.json");
