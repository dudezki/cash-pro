<template>
  <AuthenticatedLayout>
    <div class="px-4 py-6 sm:px-0">
      <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6">Company Management</h1>
        
        <div v-if="loading" class="text-center py-8">Loading...</div>
        <div v-else-if="error" class="text-red-600 mb-4">{{ error }}</div>
        
        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Name
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Slug
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Database
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="company in companies" :key="company.id">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                  {{ company.name }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ company.slug }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    v-if="company.has_database"
                    class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800"
                  >
                    {{ company.database_name }}
                  </span>
                  <span
                    v-else
                    class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800"
                  >
                    No Database
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    v-if="!company.has_database"
                    @click="handleCreateDb(company.id)"
                    class="text-indigo-600 hover:text-indigo-900"
                  >
                    Create DB
                  </button>
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
import { adminService, type Company } from '../services/admin'
import AuthenticatedLayout from '../components/layouts/AuthenticatedLayout.vue'

const companies = ref<Company[]>([])
const loading = ref(true)
const error = ref('')

async function fetchCompanies() {
  loading.value = true
  error.value = ''
  try {
    companies.value = await adminService.listCompanies()
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to load companies'
  } finally {
    loading.value = false
  }
}

async function handleCreateDb(companyId: number) {
  try {
    await adminService.createTenantDb(companyId)
    await fetchCompanies() // Refresh list
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to create database'
  }
}

onMounted(() => {
  fetchCompanies()
})
</script>

<style scoped>
</style>

