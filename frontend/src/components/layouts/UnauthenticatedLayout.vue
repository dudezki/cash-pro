<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
    <div class="flex items-center justify-center min-h-screen p-4">
      <div
        v-motion
        :initial="{ opacity: 0, y: 20 }"
        :enter="{ opacity: 1, y: 0, transition: { duration: 0.5 } }"
        class="w-full max-w-md"
      >
        <slot />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
</style>

