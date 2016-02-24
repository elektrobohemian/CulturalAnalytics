var w = 1500, //3000,
    h = 1000 //3000,
fill = d3.scale.category20();

overviewJSONpath = "century_test.json";
//overviewJSONpath="century.json"

document.body.addEventListener('keydown', function (e) {
    k = e.keyCode;
    if (k == 37 || k == 8) { // react on "left cursor" and "backspace"
        renderNetworkGraph(overviewJSONpath);
    }
});


// takes an input raw string and encodes all special characters as HTML entities
function cleanUp(rawStr) {
    if (rawStr == "nan") {
        return "- Unknown -";
    } else
        return rawStr.replace(/[\u00A0-\u9999<>\&]/gim, function (i) {
            return '&#' + i.charCodeAt(0) + ';';
        });
}


function renderNetworkGraph(jsonFileName) {
    imgDir = "../tmp/"
    d3.select("#chart").selectAll("*").remove();

    var vis = d3.select("#chart")
        .append("svg:svg")
        .attr("width", w)
        .attr("height", h);

    d3.json(jsonFileName, function (json) {
        var force = d3.layout.force()
            .charge(-120)
            .linkDistance(100)
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
            .attr("class", function (d) {
                if (d.type == "century" || d.type == "dateClean") return "node";
                else return "nodeInvisible";
            })
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
                if (d.type == "century" || d.type == "dateClean") return "centurylabels";
                else return "labels";
            })
            .text(function (d) {
                if (d.type == "century") return d.name + "th";
                else if (d.type == "dateClean") return d.name;
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
                if (d.type != "century" && d.type != "dateClean") {
                    if (d.imagePath != "undefined")
                        return imgDir + d.imagePath + ".jpg";
                    else
                        return "./blank.png";
                }
            })
            .attr("x", function (d) {
                return d.x;
            })
            .attr("y", function (d) {
                return d.y;
            })
            .attr("height", 50)
            .attr("width", 50)
            .on("click", function (d, i) {
                var pos = d3.mouse(this);
                console.log(pos);
                console.log(d.name);
                event.preventDefault();
            })
            .on("dblclick", function (d) {
                renderNetworkGraph("./clusters/" + d.century + "/" + d.cluster + ".json");
            })
            .on("contextmenu", function (d, i) {
                //handle right click
                linkHead = "http://ngcs.staatsbibliothek-berlin.de/?action=metsImage&format=jpg&metsFile=";
                linkTail = "&divID=PHYS_0001"; //&width=800&rotate=0";
                sbbViewerLink = "http://digital.staatsbibliothek-berlin.de/werkansicht/?PPN=";
                metsLink = "http://digital.staatsbibliothek-berlin.de/metsresolver/?PPN=";
                ppnLink = "http://stabikat.de/DB=1/PPN?PPN=";

                $("#myDialogText").empty();
                $("#myDialogText").append("<img height='170px' src='" + imgDir + d.imagePath + ".jpg' />");
                $("#myDialogText").append("<br /><button type='button' onclick=\"renderNetworkGraph('./clusters/" + d.century + "/" + d.cluster + ".json');$('#dialog').dialog('close');\">Inspect cluster</button>");
                $("#myDialogText").append("<p><b>" + cleanUp(d.title) + "</b></p>");
                $("#myDialogText").append("<p>Creator: " + cleanUp(d.creator) + "</p>");
                $("#myDialogText").append("<p>Spatial: " + d.location + "</p>");
                console.log(d.century + ": " + d.cluster);

                $("#linkList").empty();
                $("#linkList").append("<li><a target='_blank' href='" + sbbViewerLink + d.name + "'>View in SBB viewer</a></li>");
                $("#linkList").append("<li><a target='_blank' href='" + linkHead + d.name + linkTail + "'>View in full size</a></li>");
                $("#linkList").append("<li><a target='_blank' href='" + metsLink + d.name + "'>METS/MODS metadata</a></li>");
                $("#linkList").append("<li><a target='_blank' href='" + ppnLink + d.name.replace("PPN", "") + "'>Show in catalog</a></li>");
                $("#dialog").dialog("open");
                //stop showing browser menu
                d3.event.preventDefault();
            })
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

renderNetworkGraph(overviewJSONpath);
