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

function draw(data) {
    // Delete all items
    // Walls
    for (let i = 0; i < items["walls"].length; i++) {
        items["walls"][i].setMap(null);
    };
    items["walls"].length = 0;
    // Gates
    for (let i = 0; i < items["gates"].length; i++) {
        items["gates"][i].setMap(null);
    };
    items["gates"].length = 0;
    // No fly zones
    for (let i = 0; i < items["no_fly"].length; i++) {
        items["no_fly"][i].setMap(null);
    };
    items["no_fly"].length = 0;

    // Create new items
    // Gates
    for (let i = 0; i < data["gates"].length; i++) {
        items["gates"].push(new google.maps.Polyline({
            path: arrayToLatLng(data["gates"][i]["points"]),
            geodesic: true,
            strokeColor: "#FFFFFF",
            strokeOpacity: 1.0,
            strokeWeight: 4,
        }));

        items["gates"][i].setMap(map)

        //return arrayToLatLng(data["gates"][i]["points"])
        //return items["gates"][0]
    };
};

function arrayToLatLng(points) {
    latLngs = [];

    for (let i = 0; i < points.length; i++) {
        latLngs.push({"lat": points[i][0], "lng": points[i][1]});
    };

    return latLngs;
};