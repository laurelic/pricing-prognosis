//Create a greyscale view layer
var lightLayer = L.tileLayer("https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoibGF1cmVsaWMiLCJhIjoiY2pteG9icGYyM3ZvaTNxbnk2a2F6MDZmciJ9.ZQhdib9of9UJDKThb3b1QA", {
    attribution: "Map data &copy; <a href=\"https://www.openstreetmap.org/\">OpenStreetMap</a> contributors, <a href=\"https://creativecommons.org/licenses/by-sa/2.0/\">CC-BY-SA</a>, Imagery © <a href=\"https://www.mapbox.com/\">Mapbox</a>",
    maxZoom: 18,
    id: "mapbox.light",
});

//initialize the hospital referral region (hrr) layer
var hrrLines = new L.layerGroup();

//initialize base maps
var baseMaps = {
    "Outline View": lightLayer
};

//initialize the layer maps

//build the map
var map = L.map("map-id", {
    center: [39.8283, -98.5795],
    zoom: 5,
    worldCopyJump: true,
    layers: [
        lightLayer,
        hrrLines,
    ]
});

//draw the hrr boundaries
d3.json(pUrl, function(data) {
    L.geoJSON(data, {
        onEachFeature: function(feature, layer) {
            layer.bindPopup(feature.properties.HRRCITY);
        },
        style: {
            color: "#18bc9c",
            weight: 2,
            fillOpacity: 0
        }
    }).addTo(hrrLines);
});

d3.json('/inpatient_data', function(data) {

});





