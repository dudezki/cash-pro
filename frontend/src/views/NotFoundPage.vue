<template>
  <AuthenticatedLayout v-if="authStore.isAuthenticated">
    <div class="flex flex-col items-center justify-center min-h-[60vh] text-center">
      <div
        v-motion
        :initial="{ opacity: 0, scale: 0.9 }"
        :enter="{ opacity: 1, scale: 1, transition: { duration: 0.5 } }"
      >
        <h1 class="text-9xl font-bold text-indigo-600 mb-4">404</h1>
        <h2 class="text-3xl font-semibold text-gray-900 dark:text-gray-100 mb-4">Page Not Found</h2>
        <p class="text-gray-600 dark:text-gray-400 mb-8 max-w-md">
          The page you're looking for doesn't exist or hasn't been implemented yet.
        </p>
        <div class="flex gap-4 justify-center">
          <router-link
            to="/dashboard"
            class="px-6 py-3 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors font-medium"
          >
            Go to Dashboard
          </router-link>
          <button
            @click="$router.go(-1)"
            class="px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-md hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors font-medium"
          >
            Go Back
          </button>
        </div>
      </div>
    </div>
  </AuthenticatedLayout>
  <UnauthenticatedLayout v-else>
    <div class="flex flex-col items-center justify-center min-h-[60vh] text-center">
      <div
        v-motion
        :initial="{ opacity: 0, scale: 0.9 }"
        :enter="{ opacity: 1, scale: 1, transition: { duration: 0.5 } }"
      >
        <h1 class="text-9xl font-bold text-indigo-600 mb-4">404</h1>
        <h2 class="text-3xl font-semibold text-gray-900 dark:text-gray-100 mb-4">Page Not Found</h2>
        <p class="text-gray-600 dark:text-gray-400 mb-8 max-w-md">
          The page you're looking for doesn't exist or hasn't been implemented yet.
        </p>
        <div class="flex gap-4 justify-center">
          <router-link
            to="/login"
            class="px-6 py-3 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors font-medium"
          >
            Go to Login
          </router-link>
          <button
            @click="$router.go(-1)"
            class="px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-md hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors font-medium"
          >
            Go Back
          </button>
        </div>
      </div>
    </div>
  </UnauthenticatedLayout>
</template>

<script setup lang="ts">
import { useAuthStore } from '../stores/auth'
import AuthenticatedLayout from '../components/layouts/AuthenticatedLayout.vue'
import UnauthenticatedLayout from '../components/layouts/UnauthenticatedLayout.vue'

const authStore = useAuthStore()
</script>

<style scoped>
</style>

