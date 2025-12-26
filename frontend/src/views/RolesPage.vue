<template>
  <AuthenticatedLayout>
    <div class="px-4 py-6 sm:px-0">
      <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6">Roles Management</h1>
        
        <div v-if="loading" class="text-center py-8">Loading...</div>
        <div v-else-if="error" class="text-red-600 mb-4">{{ error }}</div>
        
        <div v-else>
          <div class="mb-6">
            <button
              @click="showCreateForm = true"
              class="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
            >
              Create Role
            </button>
          </div>
          
          <div v-if="showCreateForm" class="mb-6 p-4 border rounded-lg">
            <h2 class="text-lg font-semibold mb-4">Create New Role</h2>
            <form @submit.prevent="handleCreateRole" class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Name</label>
                <input
                  v-model="newRole.name"
                  type="text"
                  required
                  class="w-full px-4 py-2 border border-gray-300 rounded-md"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Description</label>
                <textarea
                  v-model="newRole.description"
                  class="w-full px-4 py-2 border border-gray-300 rounded-md"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Permissions</label>
                <div class="space-y-2 max-h-40 overflow-y-auto">
                  <label
                    v-for="permission in permissions"
                    :key="permission.id"
                    class="flex items-center"
                  >
                    <input
                      type="checkbox"
                      :value="permission.id"
                      v-model="newRole.permission_ids"
                      class="mr-2"
                    />
                    <span class="text-sm">{{ permission.resource_type }}:{{ permission.action }}</span>
                  </label>
                </div>
              </div>
              <div class="flex space-x-2">
                <button
                  type="submit"
                  class="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
                >
                  Create
                </button>
                <button
                  type="button"
                  @click="showCreateForm = false"
                  class="bg-gray-200 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-300"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
          
          <div class="space-y-4">
            <div
              v-for="role in roles"
              :key="role.id"
              class="p-4 border rounded-lg"
            >
              <h3 class="text-lg font-semibold">{{ role.name }}</h3>
              <p class="text-sm text-gray-600 mb-2">{{ role.description }}</p>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="perm in role.permissions"
                  :key="perm.id"
                  class="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs"
                >
                  {{ perm.resource_type }}:{{ perm.action }}
                </span>
              </div>
            </div>
          </div>
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
const showCreateForm = ref(false)
const newRole = ref({
  name: '',
  description: '',
  permission_ids: [] as number[]
})

const roles = rbacStore.roles
const permissions = rbacStore.permissions

async function fetchData() {
  loading.value = true
  error.value = ''
  try {
    await Promise.all([
      rbacStore.fetchRoles(),
      rbacStore.fetchPermissions()
    ])
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to load data'
  } finally {
    loading.value = false
  }
}

async function handleCreateRole() {
  try {
    await rbacStore.createRole(newRole.value)
    showCreateForm.value = false
    newRole.value = { name: '', description: '', permission_ids: [] }
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to create role'
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
</style>

