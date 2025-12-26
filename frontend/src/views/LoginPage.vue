<template>
  <UnauthenticatedLayout>
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
      <h1 class="text-3xl font-bold text-center mb-6 text-gray-900 dark:text-gray-100">Login</h1>
      <form @submit.prevent="handleLogin" class="space-y-6">
        <div>
          <label for="email_or_username" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Email or Username
          </label>
          <input
            id="email_or_username"
            v-model="emailOrUsername"
            type="text"
            required
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="email@example.com or username"
          />
        </div>
        <div>
          <label for="password" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Password
          </label>
          <input
            id="password"
            v-model="password"
            type="password"
            required
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="••••••••"
          />
        </div>
        <div v-if="error" class="text-red-600 text-sm">{{ error }}</div>
        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ loading ? 'Logging in...' : 'Login' }}
        </button>
        <div class="text-center text-sm text-gray-600 dark:text-gray-400">
          Don't have an account?
          <router-link to="/register" class="text-indigo-600 hover:text-indigo-700">
            Register
          </router-link>
        </div>
      </form>
    </div>
  </UnauthenticatedLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import UnauthenticatedLayout from '../components/layouts/UnauthenticatedLayout.vue'

const router = useRouter()
const authStore = useAuthStore()

const emailOrUsername = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  loading.value = true
  error.value = ''
  
  try {
    await authStore.login(emailOrUsername.value, password.value)
    
    // Wait a tick to ensure store is updated
    await new Promise(resolve => setTimeout(resolve, 0))
    
    // Determine where to navigate
    let targetPath = '/dashboard'
    if (!authStore.isSuperAdmin && authStore.companies.length === 0) {
      targetPath = '/setup/organization'
    }
    
    // Use replace instead of push to avoid back button issues
    await router.replace(targetPath)
  } catch (err: any) {
    console.error('Login error:', err)
    const errorMessage = err.response?.data?.detail || err.message || 'Login failed. Please try again.'
    error.value = errorMessage
    // Show more details in console for debugging
    if (err.response) {
      console.error('Response status:', err.response.status)
      console.error('Response data:', err.response.data)
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
</style>

