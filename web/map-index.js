// Walls
function makeWall() {
    mode = "wall";

    points = [];
}

function editWall(index) {
    mode = "wall_edit";

    deselectWall();

    items["walls"][index].setOptions({
        editable: true,
        strokeColor: "#ff96ff",
    });
}

function saveWall(index=null) {
    if (index == null) {
        item = line;

        line.setMap(null);
    } else {
        item = items["walls"][index];
    };

    path = item.getPath().getArray();
    coords = [];

    for (let i = 0; i < path.length; i++) {        
        coords.push([path[i].lat(), path[i].lng()]);
    };

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

    selected_wall.push(drawLine(points, "#0F0", 10));
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

function editGate(index) {
    mode = "gate_max"


}

function saveGate() {
    mode = null;

    points = [];

    for (let i = 0; i < markers.length; i++) {
        let pos = markers[i].getPosition();

        points.push([pos.lat(), pos.lng()])
    }

    deleteItems(markers);

    return points;
}

function selectGate(points) {
    try {
        deleteItems(selected_gate);
    } catch (e) {}

    selected_gate.push(drawLine(points, "#000", 10));
    selected_gate.push(addMarker(points[0], "#000", 7, 1));
    selected_gate.push(drawLine(points, "#FF0", 4));
    selected_gate.push(addMarker(points[0], "#FF0", 4, 1));
}

function deselectGate() {
    try {
        deleteItems(selected_gate);
    } catch (e) {}
}