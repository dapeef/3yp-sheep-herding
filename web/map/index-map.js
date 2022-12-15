function makeGate() {
    mode = "gate";

    points = [];
};

function saveGate() {
    mode = null;

    // Delete all markers
    for (let i = 0; i < markers.length; i++) {
        markers[i].setMap(null);
    };
    markers.length = 0;

    return points;
}