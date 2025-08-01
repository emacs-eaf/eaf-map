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
       distanceLabels: [],
       polyline: null,
       showDistanceTip: false,
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
   },
   mounted() {
     window.initMap = this.initMap;
     window.addNewPlace = this.addNewPlace;
     window.updatePlaces = this.updatePlaces;
     window.toggleDistanceTip = this.toggleDistanceTip;
     window.zoomIn = this.zoomIn;
     window.zoomOut = this.zoomOut;
     window.moveUp = this.moveUp;
     window.moveDown = this.moveDown;
     window.moveLeft = this.moveLeft;
     window.moveRight = this.moveRight;
   },
   methods: {
     initMap(markerIconPath) {
       L.Marker.prototype.options.icon = L.icon({
         iconRetinaUrl: markerIconPath,
         iconUrl: markerIconPath,
         iconSize: [25, 18],
         iconAnchor: [12, 10],
         popupAnchor: [1, -34],
         tooltipAnchor: [16, -28],
         shadowSize: [41, 41],
       });

       if (navigator.geolocation) {
         navigator.geolocation.getCurrentPosition(position => {
           this.currentLatitude = position.coords.latitude;
           this.currentLongitude = position.coords.longitude;
         });
       }

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

       this.cleanLabels();

       this.cleanDistanceLabels();

       for (let i = 0; i < places.length; i++) {
         const marker = this.buildMarker(places[i][2], places[i][1]);
         this.markers.push(marker);
       }
       this.drawPaths();
     },

     addNewPlace(placeName, placeLongitude, placeLatitude, order) {
       if (order == -1) {
         this.places.push([placeName, placeLongitude, placeLatitude]);

         const marker = this.buildMarker(placeLatitude, placeLongitude);
         this.markers.push(marker);
       } else {
         this.places.splice(order, 0, [placeName, placeLongitude, placeLatitude]);

         const marker = this.buildMarker(placeLatitude, placeLongitude);
         this.markers.splice(order, 0, marker);
       }

       this.updatePlaces(this.places);
     },

     zoomIn() {
       if (this.map) {
         this.map.zoomIn();
       }
     },

     zoomOut() {
       if (this.map) {
         this.map.zoomOut();
       }
     },

     moveUp() {
       if (this.map) {
         const currentCenter = this.map.getCenter();
         const newCenter = [currentCenter.lat - 1, currentCenter.lng];
         this.map.panTo(newCenter);
       }
     },

     moveDown() {
       if (this.map) {
         const currentCenter = this.map.getCenter();
         const newCenter = [currentCenter.lat + 1, currentCenter.lng];
         this.map.panTo(newCenter);
       }
     },

     moveLeft() {
       if (this.map) {
         const currentCenter = this.map.getCenter();
         const newCenter = [currentCenter.lat, currentCenter.lng - 1];
         this.map.panTo(newCenter);
       }
     },

     moveRight() {
       if (this.map) {
         const currentCenter = this.map.getCenter();
         const newCenter = [currentCenter.lat, currentCenter.lng + 1];
         this.map.panTo(newCenter);
       }
     },

     buildMarker(placeLatitude, placeLongitude) {
       const marker = L.marker([placeLatitude, placeLongitude]).addTo(this.map);
       return marker;
     },

     cleanLabels() {
       for (let i = 0; i < this.labels.length; i++) {
         this.map.removeLayer(this.labels[i]);
       }
       this.labels = [];
     },

     cleanDistanceLabels() {
       for (let i = 0; i < this.distanceLabels.length; i++) {
         this.map.removeLayer(this.distanceLabels[i]);
       }
       this.distanceLabels = [];
     },

     toggleDistanceTip() {
       this.cleanDistanceLabels();

       this.showDistanceTip = !this.showDistanceTip;
       this.drawDistancelabels();

       if (this.showDistanceTip === true) {
         window.pyobject.send_message_to_emacs("Show distance labels");
       } else {
         window.pyobject.send_message_to_emacs("Hide distance labels");
       }
     },

     drawDistancelabels() {
       if (this.showDistanceTip === true) {
         for (let i = 0; i < this.infoLen; i++) {
           const distanceLabel = L.marker(
             [(this.waypoints[i].location[1] + this.waypoints[i + 1].location[1]) / 2,
              (this.waypoints[i].location[0] + this.waypoints[i + 1].location[0]) / 2], {
                icon: L.divIcon({
                  iconSize: [150, 20],
                  className: "distance-label",
                  html: "<div>" + "<div>" + (this.legs[i].distance / 1000).toFixed(1) + "公里 / " + (this.legs[i].duration / 3600.0).toFixed(1) + "小时" + "</div>" + "</div>"
                })
           }).addTo(this.map);
           this.distanceLabels.push(distanceLabel);
         }
       }
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

                 this.legs = data.routes[0].legs;
                 this.waypoints = data.waypoints;
                 this.infoLen = this.waypoints.length - 1;

                 var distanceCount = 0;
                 var durationCount = 0;
                 for (let i = 0; i < this.waypoints.length; i++) {
                   const placeName = this.places[i][0].split(",")[0];

                   /* Don't show marker if last place is same as first place */
                   if (i === this.waypoints.length - 1 && this.places[i][0] === this.places[0][0]) {
                     continue;
                   }

                   const placeIndex = i + 1;
                   const placeLabel = L.marker([this.waypoints[i].location[1], this.waypoints[i].location[0]], {
                     icon: L.divIcon({
                       iconSize: [150, 65],
                       className: "place-label",
                       html: "<div>" + "<div style='text-shadow: 0 0 0.2em #F8FE29, 0 0 0.2em #F8FE29, 0 0 0.2em #F8FE29'>" + placeIndex + " " + placeName + "</div>" + "</div>"
                     })
                   }).addTo(this.map);
                   this.labels.push(placeLabel);
                 }

                 this.drawDistancelabels();

                 for (let i = 0; i < this.infoLen; i++) {
                   distanceCount += this.legs[i].distance;
                   durationCount += this.legs[i].duration;
                 }

                 this.totalNumber = this.waypoints.length;
                 this.totalDistance = (distanceCount / 1000).toFixed(1);
                 this.totalCost = (durationCount / 3600.0).toFixed(1);

                 this.polyline = new L.Polyline(polyline.decode(data.routes[0].geometry), {color: '#3DB3D0'}).addTo(this.map);
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
   font-size: 14px;
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
   font-size: 14px;
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
