<template>
  <div
    id="mapContainer"
    class="h-full w-full">
  </div>
</template>

<script>
 import { QWebChannel } from "qwebchannel";
 import "leaflet/dist/leaflet.css";
 import polyline from 'polyline';
 import L from "leaflet";

 export default {
   name: "LeafletMap",
   data() {
     return {
       map: null,
       places: [],
       markers: [],
       polyline: null,
       currentLatitude: 39,
       currentLongitude: 104
     };
   },
   watch: {
     places: {
       // eslint-disable-next-line no-unused-vars
       handler: function(val, oldVal) {
         window.pyobject.vue_update_places(val);
       },
       deep: true
     }
   },
   created() {
     // eslint-disable-next-line no-undef
     new QWebChannel(qt.webChannelTransport, channel => {
       window.pyobject = channel.objects.pyobject;
     });

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

     if (navigator.geolocation) {
       navigator.geolocation.getCurrentPosition(position => {
         this.currentLatitude = position.coords.latitude;
         this.currentLongitude = position.coords.longitude;
       });

       this.initMap();
     } else {
       this.initMap();
     }
   },
   methods: {
     initMap() {
       this.map = L.map("mapContainer", {
         attributionControl: false,
         zoomControl: false
       }).setView([this.currentLatitude, this.currentLongitude], 5);

       L.tileLayer("http://{s}.tile.osm.org/{z}/{x}/{y}.png", {
       }).addTo(this.map);
     },

     addNewPlace(placeName, placeLongitude, placeLatitude) {
       this.places.push([placeName, placeLongitude, placeLatitude]);

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
