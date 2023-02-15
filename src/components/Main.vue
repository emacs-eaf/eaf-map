<template>
  <div id="mapContainer"></div>
</template>

<script>
 import "leaflet/dist/leaflet.css";
 import L from "leaflet";

 export default {
   name: "LeafletMap",
   data() {
     return {
       map: null,
     };
   },
   mounted() {
     this.map = L.map("mapContainer", {
       zoomControl: false
     }).setView([46.05, 11.05], 5);

     L.tileLayer("http://{s}.tile.osm.org/{z}/{x}/{y}.png", {
     }).addTo(this.map);

     L.control.zoom({
       position: "bottomright"
     }).addTo(this.map);
   },
   onBeforeUnmount() {
     if (this.map) {
       this.map.remove();
     }
   },
 };
</script>

<style scoped>
 #mapContainer {
   width: 100vw;
   height: 100vh;
 }
</style>
