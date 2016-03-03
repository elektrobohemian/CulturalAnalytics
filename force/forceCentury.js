/*
Nice unicode characters:
&#8226; bullet
&#8227; triangular bullet
&#8718; black box (QED)
&#9210; black circle (record)
&#9209; black square (stop)
&#9608; full black block
*/
// dimensions of the SVG canvas
var w = 1600, //3000,
    h = 1100 //3000,
fill = d3.scale.category20();

//var overviewJSONpath = "century_test.json";
var overviewJSONpath = "century.json"

// flag showing if the user is currently inspecting a cluster
var inClusterInspection = false;

// a "dictionary" containing related nodes with respect to the current node
var relatedNodes = {};

// display settings object for comparison edges
var displayComparisonEdge = {};

// path to images
imgDir = "../tmp/"

legendCreated = false;

// the force layout
var force;

var linkHead = "http://ngcs.staatsbibliothek-berlin.de/?action=metsImage&format=jpg&metsFile=";
var linkTail = "&divID=PHYS_0001"; //&width=800&rotate=0";
var sbbViewerLink = "http://digital.staatsbibliothek-berlin.de/werkansicht/?PPN=";
var metsLink = "http://digital.staatsbibliothek-berlin.de/metsresolver/?PPN=";
var ppnLink = "http://stabikat.de/DB=1/PPN?PPN=";
var oaiGetRecordLink = "http://digital.staatsbibliothek-berlin.de/oai/?verb=GetRecord&metadataPrefix=mets&identifier=oai:digital.staatsbibliothek-berlin.de:";
var oaiGetRecordLink_DC = "http://digital.staatsbibliothek-berlin.de/oai/?verb=GetRecord&metadataPrefix=oai_dc&identifier=oai:digital.staatsbibliothek-berlin.de:";
var stabikatSearchLink = "http://stabikat.de/DB=1/SET=1/TTL=1/CMD?ACT=SRCHA&IKT=1016&SRT=YOP&TRM=";
var stabikatPlusLink = "http://eds.b.ebscohost.com/eds/results?vid=0&hid=113&bdata=JmNsaTA9RlQxJmNsdjA9WSZsYW5nPWRlJnR5cGU9MCZzaXRlPWVkcy1saXZl&bquery="
    /* OLD comparison of two elements
    var queue = [];
    var queueData = [];
    */
var queue = null;
var queueData = null;

var locations = [
                ['Bondi Beach', -33.890542, 151.274856, 4],
                ['Coogee Beach', -33.923036, 151.259052, 5],
                ['Cronulla Beach', -34.028249, 151.157507, 3],
                ['Manly Beach', -33.80010128657071, 151.28747820854187, 2],
                ['Maroubra Beach', -33.950198, 151.259302, 1]
            ];

document.body.addEventListener('keydown', function (e) {
    k = e.keyCode;
    if (k == 37 || k == 8) { // react on "left cursor" and "backspace"
        backToOverview();
    } else if (k == 27) {
        // remove old lines
        d3.selectAll("#compareEdge").remove();
    } else if (k == 66) { // 'b'
        createDownloadWindow();
    } else if (k == 67) { // 'c'
        drawSimilarityEdges();
    } else if (k == 68) { // 'd'
        if (queueData != null)
            displayDetailDialog(queueData, 0);
    } else if (k == 77) { // 'm'
        locations = [];
        d3.selectAll("image").each(function (d) {
            if (d.lat != "nan") {
                locArray = [];
                locArray.push(d.source + " (" + d.location + ")");
                locArray.push(d.lat);
                locArray.push(d.lng);
                locArray.push(imgDir + d.imagePath + ".jpg");
                locArray.push(d);
                locations.push(locArray);
            }
        });
        $("#dialogMap").dialog("open");
        initMap();

    } else if (k == 80) { // p
        force.stop();
    } else if (k == 83) { // s
        force.start();
    } else if (k == 191) { // ?
        $("#dialogHelp").dialog("open");
    }
    console.log(k);
});


function drawSimilarityEdges() {
    // stop the animation in order to draw the lines without the need for updating them continuously
    force.stop();
    // remove old lines
    d3.selectAll("#compareEdge").remove();
    // remove old related nodes
    for (var member in relatedNodes) delete relatedNodes[member];

    vis = d3.select("#chart svg");

    d3.selectAll("image").each(function (d) {
        Object.keys(d).forEach(function (key, index) {
            // key: the name of the object key
            // index: the ordinal position of the key within the object 
            // type, weight, fixed are ignored
            if (key != "type" && key != "weight" && key != "fixed" && key != "century") {
                if (queueData != null) {
                    if (eval("queueData." + key) == eval("d." + key) && displayComparisonEdge[key] == "on") {

                        vis.append("svg:line")
                            //.attr("class", "link")
                            .attr("class", "edgeLink_" + key)
                            .attr("id", "compareEdge")
                            //.style("stroke-width", 1)
                            .attr("x1", queueData.x)
                            .attr("y1", queueData.y)
                            .attr("x2", d.x)
                            .attr("y2", d.y);

                        if (!(d.name in relatedNodes)) {
                            relatedNodes[d.name] = d;
                            console.log("Added " + d.name);
                        }
                    }
                }
            }
        });
    }); // END selectAll + foreach
}

function backToOverview() {
    inClusterInspection = false;
    queue = null;
    queueData = null;
    // remove old related nodes
    for (var member in relatedNodes) delete relatedNodes[member];

    renderNetworkGraph(overviewJSONpath);
}

function createDownloadWindow() {
    sample = {
        "publisher": "Drucker des Bollanus",
        "imagePath": "PPN788641328",
        "century": 14,
        "name": "PPN788641328",
        "title": "De conceptione Beatae Virginis Mariae",
        "locationRaw": "Erfurt",
        "creator": "Bollanus, Dominicus",
        "mediatype": "Monograph",
        "cluster": "10",
        "source": "Bollanus, Dominicus: De conceptione Beatae Virginis Mariae. Erfurt  Berlin 1486",
        "dateClean": "1486",
        "alternative": "nan",
        "subject": "Historische Drucke",
        "type": "image",
        "id": "PPN788641328",
        "location": "Erfurt"
    }
    var w = window.open();
    var html = "<!DOCTYPE html><html><head><meta http-equiv='Content-Type' content='text/html; charset=utf-8'/><link type='text/css' rel='stylesheet' href='force.css' /></head><body></body></html>";

    var htmlHead = "<!DOCTYPE html><html><head><meta http-equiv='Content-Type' content='text/html; charset=utf-8'/><link type='text/css' rel='stylesheet' href='force.css' /></head><body>";
    var htmlBody = "";
    var htmlTail = "</body></html>";

    w.document.writeln(html);
    $(w.document.body).append("<h2>List of Related Media</h2>");
    for (var member in relatedNodes) {
        /* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
         TODO
         Tabelle mit maschinellen Korrekturen aus JSON anreichern
        * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */
        $(w.document.body).append("<p>" + relatedNodes[member].source + "</p>");
        $(w.document.body).append("<a target='_blank' href='" + oaiGetRecordLink + relatedNodes[member].name + "'>METS/MODS</a> ");
        $(w.document.body).append("<a target='_blank' href='" + oaiGetRecordLink_DC + relatedNodes[member].name + "'>Dublin Core</a>");
        htmlBody = htmlBody + "<p>" + relatedNodes[member].source + "</p>";
        htmlBody = htmlBody + "<a target='_blank' href='" + oaiGetRecordLink + relatedNodes[member].name + "'>METS/MODS</a> "
        htmlBody = htmlBody + "<a target='_blank' href='" + oaiGetRecordLink_DC + relatedNodes[member].name + "'>Dublin Core</a>";
    };
    //download("test.html", htmlHead + htmlBody + htmlTail);
}

function download(filename, text) {
    // source: http://stackoverflow.com/questions/3665115/create-a-file-in-memory-for-user-to-download-not-through-server
    var element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    element.setAttribute('download', filename);

    element.style.display = 'none';
    document.body.appendChild(element);

    element.click();

    document.body.removeChild(element);
}

function createGoogleMapsLink(lat, lng) {
    return "http://maps.google.com/maps?q=" + lat + "," + lng;
}

// takes an input raw string and encodes all special characters as HTML entities
function cleanUp(rawStr) {
    if (rawStr == "nan") {
        return "- Unknown -";
    } else
        return rawStr.replace(/[\u00A0-\u9999<>\&]/gim, function (i) {
            return '&#' + i.charCodeAt(0) + ';';
        });
}

function displaySettingsDialog() {
    sample = {
        "publisher": "Drucker des Bollanus",
        //"imagePath": "PPN788641328",
        //"century": 14,
        //"name": "PPN788641328",
        "title": "De conceptione Beatae Virginis Mariae",
        //"locationRaw": "Erfurt",
        "creator": "Bollanus, Dominicus",
        "mediatype": "Monograph",
        //"cluster": "10",
        "source": "Bollanus, Dominicus: De conceptione Beatae Virginis Mariae. Erfurt  Berlin 1486",
        "dateClean": "1486",
        "alternative": "nan",
        "subject": "Historische Drucke",
        //"type": "image",
        //"id": "PPN788641328",
        "location": "Erfurt"
    }

    $("#dlgSettingsText").empty();

    Object.keys(displayComparisonEdge).forEach(function (key, index) {
        if (key != "id" && key != "lat" && key != "lng" && key != "cluster" && key != "type" && key != "imagePath" && key != "century" && key != "name" && key != "locationRaw") {
            $('#dlgSettingsText').append("<span class='legend_" + key + "'>&#9608;&nbsp;</span>" + '<input type="button" id="' + key + '" value="' + key + '" class="' + displayComparisonEdge[key] + '" onfocus="blur();" onclick="toggleButton(this); drawSimilarityEdges();" /> <br />');
        }
    });
    //$('dlgSettingsText').append("<p>XYZ</p>");
    $('#dialogSettings').dialog('open');
}

function toggleButton(el) {
    if (el.className == "on") {
        el.className = "off";
        displayComparisonEdge[el.id] = "off";
    } else {
        el.className = "on";
        displayComparisonEdge[el.id] = "on";
    }
    //console.log(el.className + " " + el.id);
}

function displayDetailDialog(d, i) {
    //handle right click
    queue = d.name;
    queueData = d;

    $("#myDialogText").empty();
    $("#myDialogText").append("<img height='150px' src='" + imgDir + d.imagePath + ".jpg' /><br />");
    if (!inClusterInspection)
        $("#myDialogText").append("<button type='button' onfocus='blur();' onclick=\"inClusterInspection=true;queue = null;queueData = null; renderNetworkGraph('./clusters/" + d.century + "/" + d.cluster + ".json');$('#dialog').dialog('close');\">Inspect cluster</button>");
    $("#myDialogText").append("&nbsp; <button type='button' onfocus='blur();' onclick=\"drawSimilarityEdges();\">Show relationships</button>");
    $("#myDialogText").append("&nbsp; <button type='button' onfocus='blur();' onclick=\"createDownloadWindow();\">Build package</button>");


    $("#myDialogText").append("<p><b>" + cleanUp(d.title) + " (" + cleanUp(d.dateClean) + ")</b></p>");
    $("#myDialogText").append("<p><span class='legend_creator'>&#9608;&nbsp;</span>Creator: " + cleanUp(d.creator) + "</p>");
    $("#myDialogText").append("<p><span class='legend_publisher'>&#9608;&nbsp;</span>Publisher: " + cleanUp(d.publisher) + "</p>");
    $("#myDialogText").append("<p><span class='legend_source'>&#9608;&nbsp;</span>Source: " + cleanUp(d.source) + "</p>");
    $("#myDialogText").append("<p><span class='legend_mediatype'>&#9608;&nbsp;</span>Mediatype: " + cleanUp(d.mediatype) + " (<span class='legend_subject'>&#9608;&nbsp;</span>" + cleanUp(d.subject) + ")</p>");

    // check if we can created a Google Maps link for the location
    if (d.lat != "nan") {
        mapURL = createGoogleMapsLink(d.lat, d.lng);
        $("#myDialogText").append("<p><span class='legend_location'>&#9608;&nbsp;</span>Spatial: <a target='_blank' href='" + mapURL + "'>" + d.location + "</a> (" + cleanUp(d.locationRaw) + ")</p>");
    } else {
        $("#myDialogText").append("<p><span class='legend_location'>&#9608;&nbsp;</span>Spatial: <em>" + d.location + "</em> (" + cleanUp(d.locationRaw) + ")</p>");
    }



    //console.log(d.century + ": " + d.cluster);

    $("#linkList").empty();
    $("#linkList").append("<li><a target='_blank' href='" + sbbViewerLink + d.name + "'>View in SBB viewer</a></li>");
    //$("#linkList").append("<li><a target='_blank' href='" + linkHead + d.name + linkTail + "'>View first scanned pagein full size</a></li>");
    $("#linkList").append("<li><a target='_blank' href='" + metsLink + d.name + "'>METS/MODS metadata</a></li>");
    $("#linkList").append("<li><a target='_blank' href='" + oaiGetRecordLink + d.name + "'>OAI-PMH METS metadata GetRecord</a></li>");
    $("#linkList").append("<li><a target='_blank' href='" + ppnLink + d.name.replace("PPN", "") + "'>Show in catalog</a></li>");
    $("#linkList").append("<li><a target='_blank' href='" + stabikatPlusLink + d.name.replace("PPN", "") + "'>Search for title in stabikat+ discovery system</a></li>");
    $("#dialog").dialog("open");
    //stop showing browser menu
    d3.event.preventDefault();
}

function initMap() {
    $("#map").empty();

    var map = new google.maps.Map(document.getElementById('map'), {
        zoom: 3,
        center: new google.maps.LatLng(52.52000659999999, 13.404954), // centers on Berlin
        mapTypeId: google.maps.MapTypeId.ROADMAP
    });

    var infowindow = new google.maps.InfoWindow();

    var marker, i;

    for (i = 0; i < locations.length; i++) {
        // in case of multiple markers at one location, we place these markes randomized around the original location
        latModifier = 1;
        lngModifier = 1;
        latOffset = Math.round(Math.random() * 10);
        lngOffset = Math.round(Math.random() * 10);
        if (latOffset % 2 == 0)
            latModifier = 1;
        else
            latModifier = -1;
        if (lngOffset % 2 == 0)
            lngModifier = 1;
        else
            lngModifier = -1;
        lat = parseFloat(locations[i][1]) + (Math.random() / 100.0) * latModifier;
        lng = parseFloat(locations[i][2]) + (Math.random() / 100.0) * lngModifier;

        marker = new google.maps.Marker({
            position: new google.maps.LatLng(lat, lng),
            map: map
        });

        google.maps.event.addListener(marker, 'click', (function (marker, i) {
            return function () {
                d = locations[i][4];
                img = "<img height='150px' src='" + locations[i][3] + "' />";

                markerContent = "";
                markerContent += "<p><b>" + cleanUp(d.title) + " (" + cleanUp(d.dateClean) + ")</b></p>";
                markerContent += "<p>" + d.location + "</p>";
                markerContent += "<p><span class='legend_creator'>&#9608;&nbsp;</span>Creator: " + cleanUp(d.creator) + "</p>";
                markerContent += "<p><span class='legend_publisher'>&#9608;&nbsp;</span>Publisher: " + cleanUp(d.publisher) + "</p>";
                markerContent += "<p><span class='legend_source'>&#9608;&nbsp;</span>Source: " + cleanUp(d.source) + "</p>";
                markerContent += "<p><span class='legend_mediatype'>&#9608;&nbsp;</span>Mediatype: " + cleanUp(d.mediatype) + " (<span class='legend_subject'>&#9608;&nbsp;</span>" + cleanUp(d.subject) + ")</p>";

                markerContent += "<ul>";
                markerContent += "<li><a target='_blank' href='" + metsLink + d.name + "'>METS/MODS metadata</a></li>";

                markerContent += "<li><a target='_blank' href='" + ppnLink + d.name.replace("PPN", "") + "'>Show in catalog</a></li>";
                markerContent += "<li><a target='_blank' href='" + stabikatPlusLink + d.location + "'>Search for location in stabikat+ discovery system</a></li>";
                markerContent += "</ul>";

                infowindow.setContent(img + markerContent);
                //infowindow.setContent(img + "<p>" + locations[i][0] + "</p>");
                infowindow.open(map, marker);
            }
        })(marker, i));
    }
}

// central D3 rendering function
function renderNetworkGraph(jsonFileName) {
    d3.select("#chart").selectAll("*").remove();

    var vis = d3.select("#chart")
        .append("svg:svg")
        .attr("width", w)
        .attr("height", h);

    d3.json(jsonFileName, function (json) {
        // after the JSON has been loaded, create a settings object in order to steer the visibility of comparison edges and create an appropriate legend
        Object.keys(json.nodes[0]).forEach(function (key, index) {
            displayComparisonEdge[key] = "on";

            if (!legendCreated) {
                $('#legend').append("<ul class='legend'>");
                if (key != "id" && key != "lat" && key != "lng" && key != "cluster" && key != "type" && key != "imagePath" && key != "century" && key != "name" && key != "locationRaw") {
                    $('#legend').append("<li class='legend'><span class='legend_" + key + "'>&#9608;&nbsp;</span>" + key + "</li>");
                }
                $('#legend').append("</ul>");
            }
        });
        legendCreated = true;


        force = d3.layout.force()
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
            //d3.select("#compareEdge").remove();
            d3.selectAll("#compareEdge").remove();
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
                return (d.x - 25);
            })
            .attr("y", function (d) {
                return (d.y - 25);
            })
            .attr("height", 50)
            .attr("width", 50)
            .on("click", function (d, i) {
                var pos = d3.mouse(this);
                console.log(pos);
                console.log(d.name);
                event.preventDefault();

                /* OLD comparison of two elements
                // only add the PPN if it is not in the queue
                if (d.name != queue[0] && d.name != queue[1] && d.type != "century") {
                    if (queue.length < 2) {
                        queue.push(d.name);
                        queueData.push(d);
                    } else {
                        queue.shift();
                        queueData.shift();
                        queue.push(d.name);
                        queueData.push(d);
                    }
                }*/
                queue = d.name;
                queueData = d;

                console.log(queue);
                console.log(queueData);
            })
            .on("dblclick", function (d) {
                if (!inClusterInspection) {
                    renderNetworkGraph("./clusters/" + d.century + "/" + d.cluster + ".json");
                    queue = null;
                    queueData = null;
                    inClusterInspection = true;
                }

            })
            .on("contextmenu", displayDetailDialog)
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
                    return d.x - 25;
                })
                .attr("y", function (d) {
                    return d.y - 25;
                });
        });
    });
};

renderNetworkGraph(overviewJSONpath);
