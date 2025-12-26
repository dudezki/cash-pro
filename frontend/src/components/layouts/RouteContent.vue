<template>
  <div class="h-full p-4 route-content-wrapper">
    <slot />
  </div>
</template>

<script setup lang="ts">
// This component exists to force Vue to recognize route changes
</script>

<style scoped>
.route-content-wrapper {
  position: relative;
}
</style>

