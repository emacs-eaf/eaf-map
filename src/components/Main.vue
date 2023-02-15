<template>
  <div
    id="mapContainer"
    class="h-full w-full">
  </div>
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
       attributionControl: false,
       zoomControl: false
     }).setView([39, 104], 5);

     L.tileLayer("http://{s}.tile.osm.org/{z}/{x}/{y}.png", {
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
</style>
