<template>
  <AuthenticatedLayout>
    <div class="px-4 py-6 sm:px-0">
      <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <div class="flex justify-between items-center mb-6">
          <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100">Subscription Plans Management</h1>
          <div class="flex gap-2">
            <button
              @click="showModuleModal = true"
              class="px-4 py-2 bg-gray-600 dark:bg-gray-700 text-white rounded-md hover:bg-gray-700 dark:hover:bg-gray-600 transition-colors text-sm font-medium"
            >
              <ion-icon name="add-outline" class="inline mr-1"></ion-icon>
              Manage Modules
            </button>
            <button
              @click="showPlanModal = true; editingPlan = null"
              class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors text-sm font-medium"
            >
              <ion-icon name="add-outline" class="inline mr-1"></ion-icon>
              Create Plan
            </button>
          </div>
        </div>

        <!-- Plans List -->
        <div v-if="loading" class="text-center py-8 text-gray-500 dark:text-gray-400">Loading plans...</div>
        <div v-else-if="error" class="text-red-600 dark:text-red-400 mb-4">{{ error }}</div>
        
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="plan in plans"
            :key="plan.id"
            class="border-2 rounded-lg p-6 transition-all"
            :class="[
              plan.is_active
                ? 'border-indigo-200 dark:border-indigo-800 bg-indigo-50/50 dark:bg-indigo-900/20'
                : 'border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50'
            ]"
          >
            <div class="flex justify-between items-start mb-4">
              <div>
                <h3 class="text-xl font-bold text-gray-900 dark:text-gray-100">{{ plan.name }}</h3>
                <p class="text-sm text-gray-500 dark:text-gray-400">{{ plan.tier }}</p>
              </div>
              <span
                class="px-2 py-1 text-xs rounded-full"
                :class="plan.is_active
                  ? 'bg-green-100 dark:bg-green-900/50 text-green-800 dark:text-green-300'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300'"
              >
                {{ plan.is_active ? 'Active' : 'Inactive' }}
              </span>
            </div>
            
            <div class="mb-4">
              <div class="text-2xl font-bold text-indigo-600 dark:text-indigo-400">
                ${{ plan.price_monthly }}
                <span class="text-sm text-gray-500 dark:text-gray-400 font-normal">/month</span>
              </div>
              <div class="text-sm text-gray-500 dark:text-gray-400">
                ${{ plan.price_annual }}/year
              </div>
            </div>
            
            <p v-if="plan.description" class="text-sm text-gray-600 dark:text-gray-400 mb-4">
              {{ plan.description }}
            </p>
            
            <div class="mb-4">
              <div class="text-xs text-gray-500 dark:text-gray-400 mb-2">Modules ({{ plan.modules.length }})</div>
              <div class="flex flex-wrap gap-1">
                <span
                  v-for="pm in plan.modules.filter(pm => pm.is_enabled)"
                  :key="pm.module_id"
                  class="px-2 py-1 text-xs bg-indigo-100 dark:bg-indigo-900/50 text-indigo-700 dark:text-indigo-300 rounded"
                >
                  {{ pm.module.name }}
                </span>
              </div>
            </div>
            
            <div class="flex gap-2 mt-4">
              <button
                @click="$router.push(`/admin/subscriptions/${plan.id}`)"
                class="flex-1 px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm"
              >
                <ion-icon name="eye-outline" class="inline mr-1"></ion-icon>
                View
              </button>
              <button
                @click="editPlan(plan)"
                class="px-3 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors text-sm"
              >
                <ion-icon name="create-outline"></ion-icon>
              </button>
              <button
                @click="deletePlan(plan.id)"
                class="px-3 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors text-sm"
              >
                <ion-icon name="trash-outline"></ion-icon>
              </button>
            </div>
          </div>
        </div>

        <!-- Plan Modal -->
        <div
          v-if="showPlanModal"
          class="fixed inset-0 bg-black/50 dark:bg-black/70 flex items-center justify-center z-50"
          @click.self="showPlanModal = false"
        >
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <h2 class="text-xl font-bold text-gray-900 dark:text-gray-100 mb-4">
              {{ editingPlan ? 'Edit Plan' : 'Create Plan' }}
            </h2>
            
            <form @submit.prevent="savePlan" class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Name</label>
                <input
                  v-model="planForm.name"
                  type="text"
                  required
                  class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Tier (unique identifier)</label>
                <input
                  v-model="planForm.tier"
                  type="text"
                  required
                  class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Description</label>
                <textarea
                  v-model="planForm.description"
                  rows="3"
                  class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                ></textarea>
              </div>
              
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Monthly Price</label>
                  <input
                    v-model.number="planForm.price_monthly"
                    type="number"
                    step="0.01"
                    required
                    class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Annual Price</label>
                  <input
                    v-model.number="planForm.price_annual"
                    type="number"
                    step="0.01"
                    required
                    class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Available Modules</label>
                <div class="max-h-48 overflow-y-auto border border-gray-300 dark:border-gray-600 rounded-md p-3 space-y-2">
                  <label
                    v-for="module in modules"
                    :key="module.id"
                    class="flex items-center space-x-2 cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      :value="module.id"
                      v-model="planForm.module_ids"
                      class="rounded border-gray-300 dark:border-gray-600 text-indigo-600 focus:ring-indigo-500"
                    />
                    <span class="text-sm text-gray-700 dark:text-gray-300">
                      {{ module.name }}
                      <span class="text-xs text-gray-500 dark:text-gray-400">({{ module.code }})</span>
                    </span>
                  </label>
                </div>
              </div>
              
              <div class="flex items-center">
                <input
                  type="checkbox"
                  v-model="planForm.is_active"
                  class="rounded border-gray-300 dark:border-gray-600 text-indigo-600 focus:ring-indigo-500"
                />
                <label class="ml-2 text-sm text-gray-700 dark:text-gray-300">Active</label>
              </div>
              
              <div class="flex justify-end gap-2 mt-6">
                <button
                  type="button"
                  @click="showPlanModal = false"
                  class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  :disabled="saving"
                  class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 transition-colors"
                >
                  {{ saving ? 'Saving...' : (editingPlan ? 'Update' : 'Create') }}
                </button>
              </div>
            </form>
          </div>
        </div>

        <!-- Module Modal -->
        <div
          v-if="showModuleModal"
          class="fixed inset-0 bg-black/50 dark:bg-black/70 flex items-center justify-center z-50"
          @click.self="showModuleModal = false"
        >
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-xl font-bold text-gray-900 dark:text-gray-100">Manage Modules</h2>
              <button
                @click="showModuleForm = true; editingModule = null"
                class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors text-sm"
              >
                <ion-icon name="add-outline" class="inline mr-1"></ion-icon>
                Add Module
              </button>
            </div>
            
            <div v-if="showModuleForm" class="mb-4 p-4 border border-gray-300 dark:border-gray-600 rounded-md">
              <h3 class="font-semibold text-gray-900 dark:text-gray-100 mb-3">
                {{ editingModule ? 'Edit Module' : 'New Module' }}
              </h3>
              <form @submit.prevent="saveModule" class="space-y-3">
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Name</label>
                  <input
                    v-model="moduleForm.name"
                    type="text"
                    required
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200 rounded-md text-sm"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Code (unique)</label>
                  <input
                    v-model="moduleForm.code"
                    type="text"
                    required
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200 rounded-md text-sm"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Category</label>
                  <input
                    v-model="moduleForm.category"
                    type="text"
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200 rounded-md text-sm"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Description</label>
                  <textarea
                    v-model="moduleForm.description"
                    rows="2"
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200 rounded-md text-sm"
                  ></textarea>
                </div>
                <div class="flex items-center">
                  <input
                    type="checkbox"
                    v-model="moduleForm.is_active"
                    class="rounded border-gray-300 dark:border-gray-600 text-indigo-600"
                  />
                  <label class="ml-2 text-sm text-gray-700 dark:text-gray-300">Active</label>
                </div>
                <div class="flex gap-2">
                  <button
                    type="submit"
                    :disabled="savingModule"
                    class="px-3 py-1 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 text-sm"
                  >
                    {{ savingModule ? 'Saving...' : (editingModule ? 'Update' : 'Create') }}
                  </button>
                  <button
                    type="button"
                    @click="showModuleForm = false; editingModule = null"
                    class="px-3 py-1 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-300 dark:hover:bg-gray-600 text-sm"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
            
            <div class="space-y-2">
              <div
                v-for="module in modules"
                :key="module.id"
                class="flex items-center justify-between p-3 border border-gray-300 dark:border-gray-600 rounded-md"
              >
                <div class="flex-1">
                  <div class="font-medium text-gray-900 dark:text-gray-100">{{ module.name }}</div>
                  <div class="text-sm text-gray-500 dark:text-gray-400">{{ module.code }}</div>
                  <div v-if="module.category" class="text-xs text-gray-400 dark:text-gray-500">{{ module.category }}</div>
                </div>
                <div class="flex items-center gap-2">
                  <span
                    class="px-2 py-1 text-xs rounded"
                    :class="module.is_active
                      ? 'bg-green-100 dark:bg-green-900/50 text-green-800 dark:text-green-300'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300'"
                  >
                    {{ module.is_active ? 'Active' : 'Inactive' }}
                  </span>
                  <button
                    @click="editModule(module)"
                    class="p-1 text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-900/30 rounded"
                  >
                    <ion-icon name="create-outline"></ion-icon>
                  </button>
                  <button
                    @click="deleteModule(module.id)"
                    class="p-1 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30 rounded"
                  >
                    <ion-icon name="trash-outline"></ion-icon>
                  </button>
                </div>
              </div>
            </div>
            
            <div class="mt-4 flex justify-end">
              <button
                @click="showModuleModal = false"
                class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-300 dark:hover:bg-gray-600"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AuthenticatedLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AuthenticatedLayout from '../components/layouts/AuthenticatedLayout.vue'
import api from '../services/api'

const route = useRoute()
const router = useRouter()

interface Plan {
  id: number
  name: string
  tier: string
  description: string | null
  price_monthly: number
  price_annual: number
  currency: string
  is_active: boolean
  modules: Array<{
    id: number
    plan_id: number
    module_id: number
    is_enabled: boolean
    module: {
      id: number
      name: string
      code: string
    }
  }>
}

interface Module {
  id: number
  name: string
  code: string
  description: string | null
  category: string | null
  is_active: boolean
}

const plans = ref<Plan[]>([])
const modules = ref<Module[]>([])
const loading = ref(true)
const error = ref('')
const showPlanModal = ref(false)
const showModuleModal = ref(false)
const showModuleForm = ref(false)
const editingPlan = ref<Plan | null>(null)
const editingModule = ref<Module | null>(null)
const saving = ref(false)
const savingModule = ref(false)

const planForm = ref({
  name: '',
  tier: '',
  description: '',
  price_monthly: 0,
  price_annual: 0,
  currency: 'USD',
  is_active: true,
  module_ids: [] as number[]
})

const moduleForm = ref({
  name: '',
  code: '',
  description: '',
  category: '',
  is_active: true
})

async function fetchPlans() {
  loading.value = true
  error.value = ''
  try {
    const response = await api.get('/api/admin/plans')
    plans.value = response.data
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to load plans'
  } finally {
    loading.value = false
  }
}

async function fetchModules() {
  try {
    const response = await api.get('/api/admin/modules')
    modules.value = response.data
  } catch (err: any) {
    console.error('Failed to load modules:', err)
  }
}

function editPlan(plan: Plan) {
  editingPlan.value = plan
  planForm.value = {
    name: plan.name,
    tier: plan.tier,
    description: plan.description || '',
    price_monthly: Number(plan.price_monthly),
    price_annual: Number(plan.price_annual),
    currency: plan.currency,
    is_active: plan.is_active,
    module_ids: plan.modules.filter(pm => pm.is_enabled).map(pm => pm.module_id)
  }
  showPlanModal.value = true
}

function editModule(module: Module) {
  editingModule.value = module
  moduleForm.value = {
    name: module.name,
    code: module.code,
    description: module.description || '',
    category: module.category || '',
    is_active: module.is_active
  }
  showModuleForm.value = true
}

async function savePlan() {
  saving.value = true
  try {
    if (editingPlan.value) {
      await api.put(`/api/admin/plans/${editingPlan.value.id}`, planForm.value)
    } else {
      await api.post('/api/admin/plans', planForm.value)
    }
    await fetchPlans()
    showPlanModal.value = false
    editingPlan.value = null
    planForm.value = {
      name: '',
      tier: '',
      description: '',
      price_monthly: 0,
      price_annual: 0,
      currency: 'USD',
      is_active: true,
      module_ids: []
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to save plan'
  } finally {
    saving.value = false
  }
}

async function saveModule() {
  savingModule.value = true
  try {
    if (editingModule.value) {
      await api.put(`/api/admin/modules/${editingModule.value.id}`, moduleForm.value)
    } else {
      await api.post('/api/admin/modules', moduleForm.value)
    }
    await fetchModules()
    showModuleForm.value = false
    editingModule.value = null
    moduleForm.value = {
      name: '',
      code: '',
      description: '',
      category: '',
      is_active: true
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to save module'
  } finally {
    savingModule.value = false
  }
}

async function deletePlan(planId: number) {
  if (!confirm('Are you sure you want to delete this plan?')) return
  try {
    await api.delete(`/api/admin/plans/${planId}`)
    await fetchPlans()
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to delete plan'
  }
}

async function deleteModule(moduleId: number) {
  if (!confirm('Are you sure you want to delete this module? This will remove it from all plans.')) return
  try {
    await api.delete(`/api/admin/modules/${moduleId}`)
    await fetchModules()
    await fetchPlans() // Refresh plans to update module lists
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to delete module'
  }
}

onMounted(async () => {
  await Promise.all([fetchPlans(), fetchModules()])
  
  // Check if we should open edit modal from query parameter
  const editId = route.query.edit
  if (editId) {
    const planId = parseInt(editId as string)
    const planToEdit = plans.value.find(p => p.id === planId)
    if (planToEdit) {
      editPlan(planToEdit)
    }
    // Remove query parameter from URL
    router.replace({ query: {} })
  }
})
</script>

