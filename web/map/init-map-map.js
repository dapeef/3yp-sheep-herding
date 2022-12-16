let map;
let last_clicked;
let mode;
let points = [];
let line;
let markers = [];
let items = {
    "walls": [],
    "gates": [],
    "no_fly": []
}

// Initialize and add the map
function initMap() {
    // The map
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 16,
        center: {lat: 51.6255863, lng: -2.5121819}, // Home
        mapTypeId: 'hybrid',
    });
    
    google.maps.event.addListener(map, 'click', function (event) {
        if (mode == null) {
            console.log("NULLLLLL");
        } else if (mode == "gate") {
            markers.push(new google.maps.Marker({
                position: event.latLng,
                map: map,
            }));

            points.push([event.latLng.lat(), event.latLng.lng()]);

            if (points.length >= 2) {
                mode = "gate_max";
            };
        } else if (mode == "wall") {
            markers.push(new google.maps.Marker({
                position: event.latLng,
                map: map,
            }));

            points.push(event.latLng);

            if (points.length >= 2) {
                mode = "wall_line";

                deleteMarkers()

                line = new google.maps.Polyline({
                    path: points,
                    editable: true,
                    geodesic: true,
                    strokeColor: "#ff96ff",
                    strokeOpacity: 1.0,
                    strokeWeight: 4,
                });
                line.setMap(map);
            };
        };
    });
};