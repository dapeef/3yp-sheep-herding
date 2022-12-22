let markers = {
    "sheep": [],
    "herding_drones": [],
    "monitor_drones": []
};

function addDots(locations, type) {
    // Delete all markers
    deleteItems(markers[type]);

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
        markers[type].push(addDot(locations[i], colour, size));
    };
}

function drawArchitecture(params) {
    // Walls, gates, no fly etc
}