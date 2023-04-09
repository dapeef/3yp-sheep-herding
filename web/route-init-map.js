let map;
let items = {
    "walls": [],
    "gates": {
        "lines": [],
        "dots": []
    },
    "no_fly": []
}

// Initialize and add the map
function initMap() {
    // The map
    map = new google.maps.Map(document.getElementById("map"), {
      zoom: 16,
      center: {lat: 51.6255863, lng: -2.5121819}, // Near Wantage
      mapTypeId: 'hybrid',
    });

    line = new google.maps.Polyline({
        path: [
            { lat: 51.625485, lng: -2.512069 },
            { lat: 51.623942, lng: -2.511199 },
            { lat: 51.623296, lng: -2.509903 },
            { lat: 51.623168, lng: -2.509662 },
            { lat: 51.623216, lng: -2.508949 },
            { lat: 51.622361, lng: -2.507511 },
            { lat: 51.622763, lng: -2.506653 },
        ],
        editable: true,
        geodesic: true,
        strokeColor: "#a6e4ff",
        strokeOpacity: 1.0,
        strokeWeight: 4,
    });
    line.setMap(map);
    
    // google.maps.event.addListener(map, 'click', function (event) {
    //     new google.maps.Marker({
    //         position: event.latLng,
    //         map: map,
    //     });
    // });
};