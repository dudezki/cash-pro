<template>
  <AuthenticatedLayout>
    <div class="space-y-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Welcome to Cash Pro!</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="bg-gray-50 dark:bg-gray-700/50 p-4 rounded-lg">
            <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Current Company</h3>
            <p v-if="authStore.currentCompany" class="text-gray-900 dark:text-gray-100 font-medium">
              {{ authStore.currentCompany.name }}
            </p>
            <p v-else class="text-gray-500 dark:text-gray-400 text-sm">No company selected</p>
          </div>
          
          <div class="bg-gray-50 dark:bg-gray-700/50 p-4 rounded-lg">
            <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">User Info</h3>
            <p class="text-gray-900 dark:text-gray-100 text-sm">{{ authStore.person?.email }}</p>
            <p v-if="authStore.isSuperAdmin" class="text-indigo-600 font-medium text-sm mt-1">
              Super Admin
            </p>
          </div>
        </div>
      </div>
    </div>
  </AuthenticatedLayout>
</template>

<script setup lang="ts">
import { useAuthStore } from '../stores/auth'
import AuthenticatedLayout from '../components/layouts/AuthenticatedLayout.vue'

const authStore = useAuthStore()
</script>

<style scoped>
</style>

