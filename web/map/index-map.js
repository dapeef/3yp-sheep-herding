function makeWall() {
    mode = "wall";

    points = [];
}

function saveWall() {
    path = line.getPath().getArray();
    coords = [];

    for (let i = 0; i < path.length; i++) {        
        coords.push([path[i].lat(), path[i].lng()]);
    };

    line.setMap(null);

    return coords;
}

function makeGate() {
    mode = "gate";

    points = [];
};

function saveGate() {
    mode = null;

    // Delete all markers
    deleteMarkers();

    return points;
}

function draw(data) {
    // Delete all items
    // Walls
    for (let i = 0; i < items["walls"].length; i++) {
        items["walls"][i].setMap(null);
    };
    items["walls"].length = 0;
    // Gates
    for (let i = 0; i < items["gates"].length; i++) {
        items["gates"][i].setMap(null);
    };
    items["gates"].length = 0;
    // No fly zones
    for (let i = 0; i < items["no_fly"].length; i++) {
        items["no_fly"][i].setMap(null);
    };
    items["no_fly"].length = 0;

    // Create new items
    // Walls
    for (let i = 0; i < data["walls"].length; i++) {
        items["walls"].push(drawLine(data["walls"][i]["points"], "#FF0"));
    };
    // Gates
    for (let i = 0; i < data["gates"].length; i++) {
        items["gates"].push(drawLine(data["gates"][i]["points"], "#FFF"));
    };
};

function arrayToLatLng(points) {
    latLngs = [];

    for (let i = 0; i < points.length; i++) {
        latLngs.push({"lat": points[i][0], "lng": points[i][1]});
    };

    return latLngs;
};

function deleteMarkers() {
    for (let i = 0; i < markers.length; i++) {
        markers[i].setMap(null);
    };
    markers.length = 0;
}

function drawLine(raw_points, colour) {
    let drawn_line = new google.maps.Polyline({
        path: arrayToLatLng(raw_points),
        geodesic: true,
        strokeColor: colour,
        strokeOpacity: 1.0,
        strokeWeight: 4,
    });

    drawn_line.setMap(map)

    return drawn_line
}