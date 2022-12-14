
function add_marker(lat, long) {
    new google.maps.Marker({
        position: {lat: lat, lng: long},
        map: map,
    });
};