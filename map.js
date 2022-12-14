// Initialize and add the map
function initMap() {
    // The map
    map = new google.maps.Map(document.getElementById("map"), {
      zoom: 9,
      center: {lat: 51.582039, lng: -1.410231}, // Near Wantage
    });
};