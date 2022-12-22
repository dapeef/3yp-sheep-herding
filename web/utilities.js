// Create circular marker or "dot"
function addDot(lat_long, colour, size, opacity=0.6) {
    let dot = new google.maps.Marker({
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

    return dot;
};

// Create ordinary marker
function addMarker(latLng) {
    let marker = new google.maps.Marker({
        position: latLng,
        map: map,
        draggable: true
    });

    return marker;
};

// Draw infrastructure - walls, gates, no-fly zones
function drawInfrastructure(data) {
    // Delete all items
    deleteItems(items["walls"]);
    deleteItems(items["gates"]["lines"]);
    deleteItems(items["gates"]["dots"]);
    deleteItems(items["no_fly"]);

    // Create new items
    // Walls
    for (let i = 0; i < data["walls"].length; i++) {
        items["walls"].push(drawLine(data["walls"][i]["points"], "#F0F"));
    };
    // Gates
    for (let i = 0; i < data["gates"].length; i++) {
        let colour = "#FF0"
        
        // Draw line of gate
        items["gates"]["lines"].push(drawLine(data["gates"][i]["points"], colour));

        // Draw spots at end of line to mark hinge end
        items["gates"]["dots"].push(addDot(data["gates"][i]["points"][0], colour, 4, 1));
    };
};

// Draw a polyline
function drawLine(raw_points, colour, thickness=4) {
    let drawn_line = new google.maps.Polyline({
        path: arrayToLatLng(raw_points),
        geodesic: true,
        strokeColor: colour,
        strokeOpacity: 1.0,
        strokeWeight: thickness,
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