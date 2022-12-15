let markers = {
    "sheep": [],
    "herding_drones": [],
    "monitor_drones": []
};

function addMarker(lat, long, colour, size) {
    let marker = new google.maps.Marker({
        position: {lat: lat, lng: long},
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
        markers[type].push(addMarker(locations[i][0], locations[i][1], colour, size));
    };
}

function drawArchitecture(params) {
    // Walls, gates, no fly etc
}