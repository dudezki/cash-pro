<template>
  <AuthenticatedLayout>
    <div class="px-4 py-6 sm:px-0">
      <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6">Permissions</h1>
        
        <div v-if="loading" class="text-center py-8">Loading...</div>
        <div v-else-if="error" class="text-red-600 mb-4">{{ error }}</div>
        
        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Resource Type
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Action
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Description
                </th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="permission in permissions" :key="permission.id">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                  {{ permission.resource_type }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ permission.action }}
                </td>
                <td class="px-6 py-4 text-sm text-gray-500">
                  {{ permission.description }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </AuthenticatedLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRbacStore } from '../stores/rbac'
import AuthenticatedLayout from '../components/layouts/AuthenticatedLayout.vue'

const rbacStore = useRbacStore()

const loading = ref(true)
const error = ref('')

const permissions = rbacStore.permissions

async function fetchPermissions() {
  loading.value = true
  error.value = ''
  try {
    await rbacStore.fetchPermissions()
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to load permissions'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchPermissions()
})
</script>

<style scoped>
</style>

