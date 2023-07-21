<template>
  <div class="box">
    <div
      id="mapContainer"
      class="h-full w-full">
    </div>
    <div class="total-box">
      <div
        v-if="totalNumber > 0"
        class="total-panel">
        途径{{totalNumber}}个地点, 总里程{{totalDistance}}公里， 总耗时{{totalCost}}小时
      </div>
    </div>
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
       currentLongitude: 104,
       totalNumber: 0,
       totalDistance: 0,
       totalCost: 0
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
             for (let i = 0; i < waypoints.length; i++) {
               const place_index = i + 1;
               const place_label = L.marker([waypoints[i].location[1], waypoints[i].location[0]], {
                 icon: L.divIcon({
                   iconSize: [150, 65],
                   className: "place-label",
                   html: "<div>" + "<div style='font-weight: bold;'>" + place_index + " " + this.places[i][0].split(",")[0] + "</div>" + "</div>"
                 })
               }).addTo(this.map);
               this.labels.push(place_label);
             }

             for (let i = 0; i < infoLen; i++) {
               const distance_label = L.marker(
                 [(waypoints[i].location[1] + waypoints[i + 1].location[1]) / 2,
                  (waypoints[i].location[0] + waypoints[i + 1].location[0]) / 2], {
                    icon: L.divIcon({
                      iconSize: [100, 16],
                      className: "distance-label",
                      html: "<div>" + "<div>" + (legs[i].distance / 1000).toFixed(1) + "公里 / " + (legs[i].duration / 3600.0).toFixed(1) + "小时" + "</div>" + "</div>"
                                                  })
               }).addTo(this.map);
               this.labels.push(distance_label);

               distanceCount += legs[i].distance;
               durationCount += legs[i].duration;
             }

             this.totalNumber = waypoints.length;
             this.totalDistance = (distanceCount / 1000).toFixed(1);
             this.totalCost = (durationCount / 3600.0).toFixed(1);

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
 .box {
   width: 100%;
   height: 100%;
 }

 ::v-deep .place-label {
   color: #333;
   display: flex;
   flex-direction: column;
   padding-left: 10px;
   height: 100%;
   width: 100%;
   justify-content: center;
   font-size: 16px;
   padding-top: 40px;
   text-align: center;
 }

 ::v-deep .distance-label {
   color: #333;
   background-color: #FCF3CFCC;
   border-radius: 5px;
   display: flex;
   flex-direction: column;
   height: 100%;
   width: 100%;
   justify-content: center;
   border: 1px solid #EDDA8F !important;
   font-size: 10px;
   text-align: center;
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

 .total-box {
   position: fixed;
   bottom: 10px;
   width: 100%;
   display: flex;
   flex-direction: row;
   align-items: center;
   justify-content: center;
   z-index: 100000;
 }

 .total-panel {
   color: #333333;
   background-color: #FFFFFFCC;
   padding-left: 10px;
   padding-right: 10px;
   border-radius: 5px;
 }
</style>
