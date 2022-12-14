let map;
let last_clicked;
let mode;
let points = [];
let line;
let markers = [];
let items = {
    "walls": [],
    "gates": {
        "lines": [],
        "dots": []
    },
    "no_fly": []
}
let selected_wall = [];
let selected_gate = [];
let selected_no_fly = [];

// Initialize and add the map
function initMap() {
    // The map
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 16,
        center: {lat: 51.6255863, lng: -2.5121819}, // Home
        mapTypeId: 'hybrid',
    });
    
    google.maps.event.addListener(map, 'click', function (event) {
        if (mode == "wall_markers") { // If in wall creation mode
            // Drop 2 markers
            markers.push(new google.maps.Marker({
                position: event.latLng,
                map: map,
            }));

            points.push(event.latLng);
            
            // When there are 2 markers, create editable polyline
            if (points.length >= 2) {
                mode = "wall_line";

                deleteItems(markers)

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
        } else if (mode == "gate") { // If in gate creation mode
            markers.push(addMarker(event.latLng))

            if (markers.length >= 2) {
                mode = "gate_max";
            };
        };
    });
};