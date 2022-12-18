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
    // Gates - lines
    for (let i = 0; i < items["gates"]["lines"].length; i++) {
        items["gates"]["lines"][i].setMap(null);
    };
    items["gates"]["lines"].length = 0;
    // Gates - dots
    for (let i = 0; i < items["gates"]["dots"].length; i++) {
        items["gates"]["dots"][i].setMap(null);
    };
    items["gates"]["dots"].length = 0;
    // No fly zones
    for (let i = 0; i < items["no_fly"].length; i++) {
        items["no_fly"][i].setMap(null);
    };
    items["no_fly"].length = 0;

    // Create new items
    // Walls
    for (let i = 0; i < data["walls"].length; i++) {
        items["walls"].push(drawLine(data["walls"][i]["points"], "#F0F"));
    };
    // Gates
    for (let i = 0; i < data["gates"].length; i++) {
        // Draw line of gate
        items["gates"]["lines"].push(drawLine(data["gates"][i]["points"], "#FF0"));

        // Draw spots at end of line to mark hinge end
        items["gates"]["dots"].push(addMarker(data["gates"][i]["points"][0], "#FF0", 4, 1));
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

function addMarker(lat_long, colour, size, opacity) {
    let marker = new google.maps.Marker({
        position: {lat: lat_long[0], lng: lat_long[1]},
        map: map,
        icon: {
            path: google.maps.SymbolPath.CIRCLE,
            fillColor: colour,
            fillOpacity: opacity,
            strokeColor: colour,
            strokeOpacity: 0.9,
            strokeWeight: 1,
            scale: size
        }
    });

    return marker;
};