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

function cancelWall() {
    if (mode == "wall_line") {
        line.setMap(null);
    } else {
        deleteItems(markers);
    }
}


function makeGate() {
    mode = "gate";

    points = [];
};

function saveGate() {
    mode = null;

    // Delete all markers
    deleteItems(markers);

    return points;
}