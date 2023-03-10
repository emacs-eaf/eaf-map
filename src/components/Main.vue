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
       labels: [],
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
     window.updatePlaces = this.updatePlaces;

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

     updatePlaces(places) {
       this.places = places;

       for (let i = 0; i < this.markers.length; i++) {
         this.map.removeLayer(this.markers[i]);
       }
       this.markers = [];

       for (let i = 0; i < this.labels.length; i++) {
         this.map.removeLayer(this.labels[i]);
       }
       this.labels = [];

       for (let i = 0; i < places.length; i++) {
         const marker = L.marker([places[i][2], places[i][1]]).addTo(this.map);
         this.markers.push(marker);
       }
       this.drawPaths();
     },

     addNewPlace(placeName, placeLongitude, placeLatitude) {
       this.places.push([placeName, placeLongitude, placeLatitude]);

       const marker = L.marker([placeLatitude, placeLongitude]).addTo(this.map);
       this.markers.push(marker);

       this.drawPaths();
     },

     drawPaths() {
       if (this.markers.length >= 2) {
         const latlngs = this.markers.map(marker => marker.getLatLng());
         if (this.polyline) {
           this.map.removeLayer(this.polyline);
         }

         const latlngsArg = latlngs.map((latlng) => latlng.lng + "," + latlng.lat).join(";")
         const url = `http://router.project-osrm.org/route/v1/car/${latlngsArg}?overview=full`;

         window.pyobject.eval_emacs_function("message", ["Fetch path data..."])

         fetch(url)
               .then(response => response.json())
           .then(data => {
             window.pyobject.eval_emacs_function("message", ["Fetch path data done."])

             var legs = data.routes[0].legs;
             var waypoints = data.waypoints;

             var infoLen = waypoints.length - 1;
             var distanceCount = 0;
             var durationCount = 0;
             for (let i = 0; i < infoLen; i++) {
               const label = L.marker([(waypoints[i].location[1] + waypoints[i + 1].location[1]) / 2,
                                       (waypoints[i].location[0] + waypoints[i + 1].location[0]) / 2], {
                 icon: L.divIcon({
                   iconSize: [120, 65],
                   className: "place-label",
                   html: "<div>" + "<div style='font-weight: bold;'>" + this.places[i][0].split(",")[0] + "-" + this.places[i + 1][0].split(",")[0] + "</div>" + "<div>" + (legs[i].distance / 1000).toFixed(1) + "??????" + "</div>" + "<div>" + " " + (legs[i].duration / 3600.0).toFixed(1) + "??????" + "</div>" + "</div>"
                 })
               }).addTo(this.map);
               this.labels.push(label);

               distanceCount += legs[i].distance;
               durationCount += legs[i].duration;
             }

             const label = L.marker(
               [waypoints[0].location[1] - 0.5, waypoints[0].location[0]], {
                  icon: L.divIcon({
                    iconSize: [140, 65],
                    className: "count-label",
                    html: "<div>" + "<div style='font-weight: bold;'>" + "??????" + (infoLen + 1) + "?????????" + "</div>" + "<div>?????????: " + (distanceCount / 1000).toFixed(1) + "??????" + "</div>" + "<div>?????????: " + " " + (durationCount / 3600.0).toFixed(1) + "??????" + "</div>" + "</div>"
                  })
             }).addTo(this.map);
             this.labels.push(label);


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
 ::v-deep .place-label {
   color: #333;
   background-color: #FCF3CF;
   border-radius: 10px;
   display: flex;
   flex-direction: column;
   padding-left: 10px;
   height: 100%;
   width: 100%;
   justify-content: center;
   border: 1px solid #EDDA8F !important;
 }

 ::v-deep .count-label {
   color: #333;
   background-color: #FCF3CF;
   border-radius: 10px;
   display: flex;
   flex-direction: column;
   padding-left: 10px;
   height: 100%;
   width: 100%;
   justify-content: center;
   border: 1px solid #EDDA8F !important;
 }
</style>
