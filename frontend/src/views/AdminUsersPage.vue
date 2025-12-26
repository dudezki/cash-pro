<template>
  <AuthenticatedLayout>
    <div class="px-4 py-6 sm:px-0">
      <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <div class="flex justify-between items-center mb-6">
          <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100">User Management</h1>
          <button
            @click="showCreateModal = true"
            class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors text-sm font-medium"
          >
            <ion-icon name="add-outline" class="inline mr-1"></ion-icon>
            Create User
          </button>
        </div>
        
        <div v-if="loading" class="text-center py-8 text-gray-500 dark:text-gray-400">Loading...</div>
        <div v-else-if="error" class="text-red-600 dark:text-red-400 mb-4">{{ error }}</div>
        
        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Email
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Username
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Name
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="user in users" :key="user.id">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                  {{ user.email }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  {{ user.username || '-' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  {{ user.first_name }} {{ user.last_name }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    v-if="user.is_super_admin"
                    class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-purple-100 text-purple-800"
                  >
                    Super Admin
                  </span>
                  <span
                    v-else-if="user.is_active"
                    class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800"
                  >
                    Active
                  </span>
                  <span
                    v-else
                    class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800"
                  >
                    Inactive
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    @click="handleImpersonate(user.id)"
                    class="text-indigo-600 hover:text-indigo-900"
                  >
                    Act as User
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Create User Modal -->
        <div
          v-if="showCreateModal"
          class="fixed inset-0 bg-black/50 dark:bg-black/70 flex items-center justify-center z-50"
          @click.self="showCreateModal = false"
        >
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 w-full max-w-md">
            <h2 class="text-xl font-bold text-gray-900 dark:text-gray-100 mb-4">Create New User</h2>
            <form @submit.prevent="handleCreateUser" class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Email *</label>
                <input
                  v-model="userForm.email"
                  type="email"
                  required
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200 rounded-md text-sm"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Password *</label>
                <input
                  v-model="userForm.password"
                  type="password"
                  required
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200 rounded-md text-sm"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Username</label>
                <input
                  v-model="userForm.username"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200 rounded-md text-sm"
                />
              </div>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">First Name</label>
                  <input
                    v-model="userForm.first_name"
                    type="text"
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200 rounded-md text-sm"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Last Name</label>
                  <input
                    v-model="userForm.last_name"
                    type="text"
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200 rounded-md text-sm"
                  />
                </div>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Phone</label>
                <input
                  v-model="userForm.phone"
                  type="tel"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200 rounded-md text-sm"
                />
              </div>
              <div class="space-y-2">
                <label class="flex items-center">
                  <input
                    type="checkbox"
                    v-model="userForm.is_active"
                    class="rounded border-gray-300 dark:border-gray-600 text-indigo-600"
                  />
                  <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Active</span>
                </label>
                <label class="flex items-center">
                  <input
                    type="checkbox"
                    v-model="userForm.is_verified"
                    class="rounded border-gray-300 dark:border-gray-600 text-indigo-600"
                  />
                  <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Verified</span>
                </label>
                <label class="flex items-center">
                  <input
                    type="checkbox"
                    v-model="userForm.is_super_admin"
                    class="rounded border-gray-300 dark:border-gray-600 text-indigo-600"
                  />
                  <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Super Admin</span>
                </label>
              </div>
              <div class="flex gap-2 mt-4">
                <button
                  type="submit"
                  :disabled="saving"
                  class="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 transition-colors text-sm"
                >
                  {{ saving ? 'Creating...' : 'Create User' }}
                </button>
                <button
                  type="button"
                  @click="showCreateModal = false"
                  class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors text-sm"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </AuthenticatedLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { adminService, type User, type CreateUserData } from '../services/admin'
import AuthenticatedLayout from '../components/layouts/AuthenticatedLayout.vue'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const users = ref<User[]>([])
const loading = ref(true)
const error = ref('')
const showCreateModal = ref(false)
const saving = ref(false)

const userForm = ref<CreateUserData>({
  email: '',
  password: '',
  first_name: '',
  last_name: '',
  username: '',
  phone: '',
  is_active: true,
  is_verified: false,
  is_super_admin: false
})

async function fetchUsers() {
  loading.value = true
  error.value = ''
  try {
    users.value = await adminService.listUsers()
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to load users'
  } finally {
    loading.value = false
  }
}

async function handleImpersonate(userId: number) {
  try {
    await adminService.impersonateUser(userId)
    await authStore.fetchCurrentUser()
    router.push('/dashboard')
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to impersonate user'
  }
}

async function handleCreateUser() {
  saving.value = true
  error.value = ''
  try {
    await adminService.createUser(userForm.value)
    showCreateModal.value = false
    // Reset form
    userForm.value = {
      email: '',
      password: '',
      first_name: '',
      last_name: '',
      username: '',
      phone: '',
      is_active: true,
      is_verified: false,
      is_super_admin: false
    }
    // Refresh users list
    await fetchUsers()
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to create user'
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
</style>

