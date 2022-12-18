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