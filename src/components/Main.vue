<template>
  <div
    id="mapContainer"
    class="h-full w-full">
  </div>
</template>

<script>
 import "leaflet/dist/leaflet.css";
 import polyline from 'polyline';
 import L from "leaflet";

 export default {
   name: "LeafletMap",
   data() {
     return {
       map: null,
       markers: [],
       polyline: null
     };
   },
   created() {
     L.Marker.prototype.options.icon = L.icon({
       iconRetinaUrl: require("leaflet/dist/images/marker-icon-2x.png"),
       iconUrl: require("leaflet/dist/images/marker-icon.png"),
       shadowUrl: require("leaflet/dist/images/marker-shadow.png"),
       iconSize: [25, 41],
       iconAnchor: [12, 41],
       popupAnchor: [1, -34],
       tooltipAnchor: [16, -28],
       shadowSize: [41, 41],
     });
   },
   mounted() {
     window.addNewPlace = this.addNewPlace;

     this.map = L.map("mapContainer", {
       attributionControl: false,
       zoomControl: false
     }).setView([39, 104], 5);

     L.tileLayer("http://{s}.tile.osm.org/{z}/{x}/{y}.png", {
     }).addTo(this.map);
   },
   methods: {
     addNewPlace(placeName, placeLongitude, placeLatitude) {
       console.log(placeName, placeLatitude, placeLatitude);

       const marker = L.marker([placeLatitude, placeLongitude]).addTo(this.map);
       this.markers.push(marker);

       if (this.markers.length >= 2) {
         const latlngs = this.markers.map(marker => marker.getLatLng());
         if (this.polyline) {
           this.map.removeLayer(this.polyline);
         }

         const latlngsArg = latlngs.map((latlng) => latlng.lng + "," + latlng.lat).join(";")
         const url = `http://router.project-osrm.org/route/v1/car/${latlngsArg}?overview=full`;
         fetch(url)
           .then(response => response.json())
           .then(data => {
             this.polyline = new L.Polyline(polyline.decode(data.routes[0].geometry), {color: '#3DA3B4'}).addTo(this.map);
             this.map.fitBounds(this.polyline.getBounds());
           });
       }
     }
   },
   onBeforeUnmount() {
     if (this.map) {
       this.map.remove();
     }
   },
 };
</script>

<style scoped>
</style>
