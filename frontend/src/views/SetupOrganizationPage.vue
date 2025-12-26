<template>
  <AuthenticatedLayout>
    <div class="max-w-2xl mx-auto px-4 py-6">
      <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-8">
        <h1 class="text-3xl font-bold text-center mb-6 text-gray-900 dark:text-gray-100">Create Your Organization</h1>
        <p class="text-center text-gray-600 dark:text-gray-400 mb-8">
          Set up your organization to get started with Cash Pro
        </p>
        
        <form @submit.prevent="handleCreateOrganization" class="space-y-6">
          <div>
            <label for="name" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Organization Name <span class="text-red-500">*</span>
            </label>
            <input
              id="name"
              v-model="formData.name"
              type="text"
              required
              class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="My Company Inc."
            />
          </div>
          
          <div>
            <label for="legal_name" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Legal Name
            </label>
            <input
              id="legal_name"
              v-model="formData.legal_name"
              type="text"
              class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="My Company Inc. (optional)"
            />
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label for="city" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                City
              </label>
              <input
                id="city"
                v-model="formData.city"
                type="text"
                class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
            <div>
              <label for="state" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                State/Province
              </label>
              <input
                id="state"
                v-model="formData.state"
                type="text"
                class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
          </div>
          
          <div>
            <label for="country" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Country
            </label>
            <input
              id="country"
              v-model="formData.country"
              type="text"
              class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="United States"
            />
          </div>
          
          <div v-if="error" class="text-red-600 text-sm bg-red-50 p-3 rounded">{{ error }}</div>
          
          <button
            type="submit"
            :disabled="loading"
            class="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {{ loading ? 'Creating...' : 'Create Organization' }}
          </button>
        </form>
      </div>
    </div>
  </AuthenticatedLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { companyService } from '../services/company'
import { useAuthStore } from '../stores/auth'
import AuthenticatedLayout from '../components/layouts/AuthenticatedLayout.vue'

const router = useRouter()
const authStore = useAuthStore()

const formData = ref({
  name: '',
  legal_name: '',
  city: '',
  state: '',
  country: ''
})

const loading = ref(false)
const error = ref('')

async function handleCreateOrganization() {
  loading.value = true
  error.value = ''
  
  try {
    await companyService.createCompany(formData.value)
    // Refresh auth to get the new company
    await authStore.fetchCurrentUser()
    // Redirect to subscription setup
    router.push('/setup/subscription')
  } catch (err: any) {
    console.error('Organization creation error:', err)
    error.value = err.response?.data?.detail || 'Failed to create organization. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
</style>

