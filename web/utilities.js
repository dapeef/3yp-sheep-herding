// Create circular marker or "dot"
function addMarker(lat_long, colour, size, opacity=0.6) {
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


// Draw infrastructure - walls, gates, no-fly zones
function drawInfrastructure(data) {
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

// Draw a polyline
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

// Delete all items in an array
function deleteItems(items) {
    for (let i = 0; i < items.length; i++) {
        items[i].setMap(null);
    };
    items.length = 0;
}

// Takes an array of points [x, y] and returns array of points {lat: x, lng: y}
function arrayToLatLng(points) {
    latLngs = [];

    for (let i = 0; i < points.length; i++) {
        latLngs.push({"lat": points[i][0], "lng": points[i][1]});
    };

    return latLngs;
};