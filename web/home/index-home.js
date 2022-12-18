let markers = {
    "sheep": [],
    "herding_drones": [],
    "monitor_drones": []
};

function addMarker(lat_long, colour, size) {
    let marker = new google.maps.Marker({
        position: {lat: lat_long[0], lng: lat_long[1]},
        map: map,
        icon: {
            path: google.maps.SymbolPath.CIRCLE,
            fillColor: colour,
            fillOpacity: 0.6,
            strokeColor: colour,
            strokeOpacity: 0.9,
            strokeWeight: 1,
            scale: size
        }
    });

    return marker;
};

function addMarkers(locations, type) {
    // Delete all markers
    for (let i = 0; i < markers[type].length; i++) {
        markers[type][i].setMap(null);
    };
    markers[type].length = 0;

    // Draw new markers
    let colour;
    let size;
    // Choose colour and size depending on type
    if (type == 'sheep') {
        colour = '#FFF';
        size = 5;
    } else if (type == 'herding_drones') {
        colour = '#ff8080';
        size = 7;
    } else if (type == 'monitor_drones') {
        colour = '#8080ff';
        size = 7;
    };
    // Draw markers
    for (let i = 0; i < locations.length; i++) {
        markers[type].push(addMarker(locations[i], colour, size));
    };
}

function drawArchitecture(params) {
    // Walls, gates, no fly etc
}