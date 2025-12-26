<template>
  <div id="app-wrapper">
    <router-view v-if="routerReady" />
    <div v-else class="loading-screen">
      <p>Loading...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const routerReady = ref(false)

onMounted(() => {
  // Ensure router is ready
  router.isReady().then(() => {
    routerReady.value = true
  }).catch((error) => {
    console.error('Router not ready:', error)
    routerReady.value = true // Show anyway to prevent blank screen
  })
})
</script>

<style scoped>
.loading-screen {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  font-family: sans-serif;
}
</style>

