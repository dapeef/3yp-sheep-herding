// Initialize and add the map
function initMap() {
    // The map
    map = new google.maps.Map(document.getElementById("map"), {
      zoom: 16,
      center: {lat: 51.6255863, lng: -2.5121819}, // Near Wantage
      mapTypeId: 'hybrid'
    });
};