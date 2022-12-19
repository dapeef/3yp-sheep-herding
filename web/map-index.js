// Walls
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

function selectWall(points) {
    try {
        deleteItems(selected_wall);
    } catch (e) {}

    selected_wall.push(drawLine(points, "#0F0", 8));
    selected_wall.push(drawLine(points, "#F0F", 4));
}

function deselectWall() {
    try {
        deleteItems(selected_wall);
    } catch (e) {}
}



// Gates
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

function selectGate(points) {
    try {
        deleteItems(selected_gate);
    } catch (e) {}

    selected_gate.push(drawLine(points, "#0F0", 8));
    selected_gate.push(drawLine(points, "#F0F", 4));
}

function deselectGate() {
    try {
        deleteItems(selected_gate);
    } catch (e) {}
}