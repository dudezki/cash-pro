<template>
  <UnauthenticatedLayout>
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
      <h1 class="text-3xl font-bold text-center mb-6 text-gray-900 dark:text-gray-100">Register</h1>
      <form @submit.prevent="handleRegister" class="space-y-6">
        <div>
          <label for="first_name" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            First Name
          </label>
          <input
            id="first_name"
            v-model="first_name"
            type="text"
            required
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="John"
          />
        </div>
        <div>
          <label for="last_name" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Last Name
          </label>
          <input
            id="last_name"
            v-model="last_name"
            type="text"
            required
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="Doe"
          />
        </div>
        <div>
          <label for="email" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Email
          </label>
          <input
            id="email"
            v-model="email"
            type="email"
            required
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="you@example.com"
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
            minlength="8"
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
          {{ loading ? 'Registering...' : 'Register' }}
        </button>
        <div class="text-center text-sm text-gray-600 dark:text-gray-400">
          Already have an account?
          <router-link to="/login" class="text-indigo-600 hover:text-indigo-700">
            Login
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

const first_name = ref('')
const last_name = ref('')
const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function handleRegister() {
  loading.value = true
  error.value = ''
  
  try {
    await authStore.register({
      email: email.value,
      password: password.value,
      first_name: first_name.value,
      last_name: last_name.value
    })
    // Super admins don't need companies - go to dashboard
    // Regular users without companies need to set up organization
    if (authStore.isSuperAdmin) {
      router.push('/dashboard')
    } else if (authStore.companies.length === 0) {
      router.push('/setup/organization')
    } else {
      router.push('/dashboard')
    }
  } catch (err: any) {
    console.error('Registration error:', err)
    const errorMessage = err.response?.data?.detail || err.message || 'Registration failed. Please try again.'
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

