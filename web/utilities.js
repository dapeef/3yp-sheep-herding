// Create circular marker or "dot"
function addMarker(lat_long, colour, size, opacity=0.6) {
    let marker = new google.maps.Marker({
        position: {lat: lat_long[0], lng: lat_long[1]},
        map: map,
        icon: {
            path: google.maps.SymbolPath.CIRCLE,
            fillColor: colour,
            fillOpacity: opacity,
            strokeColor: colour,
            strokeOpacity: 0.9,
            strokeWeight: 1,
            scale: size
        }
    });

    return marker;
};