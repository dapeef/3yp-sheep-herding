// Walls
function makeWall() {
    mode = "wall_markers";

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
    if (mode != "wall_markers") { // If at least 2 points have been selected
        if (index == null) { // Is in making mode
            item = line;

            line.setMap(null);
        } else { // Is in editing mode
            item = items["walls"][index];
        };

        path = item.getPath().getArray();
        coords = [];

        for (let i = 0; i < path.length; i++) {
            coords.push([path[i].lat(), path[i].lng()]);
        };

        return coords;
    } else { // If 0 or 1 point has been selected
        // Delete markers
        deleteItems(markers)
        
        return null
    }
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
    mode = "gate_edit";

    deselectGate();

    line_item = items["gates"]["lines"][index];
    dot_item = items["gates"]["dots"][index];

    path = line_item.getPath().getArray();

    markers.push(addMarker(path[0]));
    markers.push(addMarker(path[1]));

    // line_item.binder = new MVCArrayBinder(line_item.getPath());
    // line_item.binder = new MVCArrayBinder(line_item.getPath());
    // dot_item.binder = new MVCArrayBinder(dot_item.getPath());

    // markers[0].bindTo('position', line_item.binder, (0).toString());
    // markers[1].bindTo('position', line_item.binder, (1).toString());

    line_item.setMap(null);
    dot_item.setMap(null);
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

function cancelGate() {
    deleteItems(markers);
}

function selectGate(points) {
    try {
        deleteItems(selected_gate);
    } catch (e) {}

    selected_gate.push(drawLine(points, "#000", 10));
    selected_gate.push(addDot(points[0], "#000", 7, 1));
    selected_gate.push(drawLine(points, "#FF0", 4));
    selected_gate.push(addDot(points[0], "#FF0", 4, 1));
}

function deselectGate() {
    try {
        deleteItems(selected_gate);
    } catch (e) {}
}



// Function to handle binding polyline to marker
// function MVCArrayBinder(mvcArray) {
//     this.array_ = mvcArray;
// }
// MVCArrayBinder.prototype = new google.maps.MVCObject();
// MVCArrayBinder.prototype.get = function (key) {
//     if (!isNaN(parseInt(key))) {
//         return this.array_.getAt(parseInt(key));
//     } else {
//         this.array_.get(key);
//     }
// }
// MVCArrayBinder.prototype.set = function (key, val) {
//     if (!isNaN(parseInt(key))) {
//         this.array_.setAt(parseInt(key), val);
//     } else {
//         this.array_.set(key, val);
//     }
// }