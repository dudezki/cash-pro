<template>
  <AuthenticatedLayout>
    <div class="px-4 py-6 sm:px-0">
      <div v-if="loading" class="text-center py-8 text-gray-500 dark:text-gray-400">Loading plan details...</div>
      <div v-else-if="error" class="text-red-600 dark:text-red-400 mb-4">{{ error }}</div>
      
      <div v-else-if="plan" class="space-y-6">
        <!-- Header -->
        <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <div class="flex justify-between items-start mb-4">
            <div>
              <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">{{ plan.name }}</h1>
              <p class="text-lg text-gray-500 dark:text-gray-400 mt-1">{{ plan.tier }}</p>
            </div>
            <div class="flex gap-2">
              <button
                @click="$router.push('/admin/subscriptions')"
                class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors text-sm"
              >
                <ion-icon name="arrow-back-outline" class="inline mr-1"></ion-icon>
                Back
              </button>
              <button
                @click="handleEdit"
                class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors text-sm"
              >
                <ion-icon name="create-outline" class="inline mr-1"></ion-icon>
                Edit Plan
              </button>
            </div>
          </div>
          
          <div class="flex items-center gap-4">
            <span
              class="px-3 py-1 rounded-full text-sm font-medium"
              :class="plan.is_active
                ? 'bg-green-100 dark:bg-green-900/50 text-green-800 dark:text-green-300'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300'"
            >
              {{ plan.is_active ? 'Active' : 'Inactive' }}
            </span>
            <span class="text-sm text-gray-500 dark:text-gray-400">
              Created: {{ formatDate(plan.created_at) }}
            </span>
          </div>
        </div>

        <!-- Statistics Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <div class="flex items-center">
              <div class="flex-shrink-0 bg-blue-100 dark:bg-blue-900/50 rounded-lg p-3">
                <ion-icon name="people-outline" class="text-2xl text-blue-600 dark:text-blue-400"></ion-icon>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Total Subscribers</p>
                <p class="text-2xl font-bold text-gray-900 dark:text-gray-100">{{ plan.total_subscribers }}</p>
              </div>
            </div>
          </div>
          
          <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <div class="flex items-center">
              <div class="flex-shrink-0 bg-green-100 dark:bg-green-900/50 rounded-lg p-3">
                <ion-icon name="checkmark-circle-outline" class="text-2xl text-green-600 dark:text-green-400"></ion-icon>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Active Subscribers</p>
                <p class="text-2xl font-bold text-gray-900 dark:text-gray-100">{{ plan.active_subscribers }}</p>
              </div>
            </div>
          </div>
          
          <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <div class="flex items-center">
              <div class="flex-shrink-0 bg-purple-100 dark:bg-purple-900/50 rounded-lg p-3">
                <ion-icon name="business-outline" class="text-2xl text-purple-600 dark:text-purple-400"></ion-icon>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Total Companies</p>
                <p class="text-2xl font-bold text-gray-900 dark:text-gray-100">{{ plan.total_companies }}</p>
              </div>
            </div>
          </div>
          
          <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <div class="flex items-center">
              <div class="flex-shrink-0 bg-indigo-100 dark:bg-indigo-900/50 rounded-lg p-3">
                <ion-icon name="apps-outline" class="text-2xl text-indigo-600 dark:text-indigo-400"></ion-icon>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Enabled Modules</p>
                <p class="text-2xl font-bold text-gray-900 dark:text-gray-100">{{ plan.enabled_modules_count }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Subscription Status Breakdown -->
        <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h2 class="text-xl font-bold text-gray-900 dark:text-gray-100 mb-4">Subscription Status Breakdown</h2>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <p class="text-2xl font-bold text-blue-600 dark:text-blue-400">{{ plan.trial_subscribers }}</p>
              <p class="text-sm text-gray-600 dark:text-gray-400">Trial</p>
            </div>
            <div class="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <p class="text-2xl font-bold text-green-600 dark:text-green-400">{{ plan.active_subscribers }}</p>
              <p class="text-sm text-gray-600 dark:text-gray-400">Active</p>
            </div>
            <div class="text-center p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
              <p class="text-2xl font-bold text-yellow-600 dark:text-yellow-400">{{ plan.cancelled_subscribers }}</p>
              <p class="text-sm text-gray-600 dark:text-gray-400">Cancelled</p>
            </div>
            <div class="text-center p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
              <p class="text-2xl font-bold text-red-600 dark:text-red-400">{{ plan.expired_subscribers }}</p>
              <p class="text-sm text-gray-600 dark:text-gray-400">Expired</p>
            </div>
          </div>
        </div>

        <!-- Pricing Information -->
        <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h2 class="text-xl font-bold text-gray-900 dark:text-gray-100 mb-4">Pricing</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Monthly Price</p>
              <p class="text-3xl font-bold text-indigo-600 dark:text-indigo-400">
                {{ plan.currency }} {{ plan.price_monthly }}
                <span class="text-lg text-gray-500 dark:text-gray-400">/month</span>
              </p>
            </div>
            <div>
              <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Annual Price</p>
              <p class="text-3xl font-bold text-indigo-600 dark:text-indigo-400">
                {{ plan.currency }} {{ plan.price_annual }}
                <span class="text-lg text-gray-500 dark:text-gray-400">/year</span>
              </p>
            </div>
          </div>
        </div>

        <!-- Plan Limits -->
        <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h2 class="text-xl font-bold text-gray-900 dark:text-gray-100 mb-4">Plan Limits</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Max Users</p>
              <p class="text-lg font-semibold text-gray-900 dark:text-gray-100">
                {{ plan.max_users ? plan.max_users : 'Unlimited' }}
              </p>
            </div>
            <div>
              <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Max Storage</p>
              <p class="text-lg font-semibold text-gray-900 dark:text-gray-100">
                {{ plan.max_storage_gb ? `${plan.max_storage_gb} GB` : 'Unlimited' }}
              </p>
            </div>
          </div>
        </div>

        <!-- Description -->
        <div v-if="plan.description" class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h2 class="text-xl font-bold text-gray-900 dark:text-gray-100 mb-4">Description</h2>
          <p class="text-gray-600 dark:text-gray-400 whitespace-pre-line">{{ plan.description }}</p>
        </div>

        <!-- Modules -->
        <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h2 class="text-xl font-bold text-gray-900 dark:text-gray-100 mb-4">
            Modules ({{ plan.enabled_modules_count }} enabled)
          </h2>
          <div v-if="plan.modules && plan.modules.length > 0" class="space-y-3">
            <div
              v-for="pm in plan.modules"
              :key="pm.id"
              class="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg"
              :class="pm.is_enabled ? 'bg-indigo-50/50 dark:bg-indigo-900/20' : 'bg-gray-50 dark:bg-gray-800/50'"
            >
              <div class="flex-1">
                <div class="flex items-center gap-2">
                  <h3 class="font-semibold text-gray-900 dark:text-gray-100">{{ pm.module.name }}</h3>
                  <span
                    class="px-2 py-0.5 text-xs rounded-full"
                    :class="pm.is_enabled
                      ? 'bg-green-100 dark:bg-green-900/50 text-green-800 dark:text-green-300'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300'"
                  >
                    {{ pm.is_enabled ? 'Enabled' : 'Disabled' }}
                  </span>
                </div>
                <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">{{ pm.module.code }}</p>
                <p v-if="pm.module.description" class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  {{ pm.module.description }}
                </p>
                <p v-if="pm.module.category" class="text-xs text-gray-400 dark:text-gray-500 mt-1">
                  Category: {{ pm.module.category }}
                </p>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-8 text-gray-500 dark:text-gray-400">
            No modules assigned to this plan
          </div>
        </div>
      </div>
    </div>
  </AuthenticatedLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { subscriptionPlanService, type SubscriptionPlanDetail } from '../services/subscription_plan'
import AuthenticatedLayout from '../components/layouts/AuthenticatedLayout.vue'

const route = useRoute()
const router = useRouter()

const plan = ref<SubscriptionPlanDetail | null>(null)
const loading = ref(true)
const error = ref('')

async function fetchPlanDetails() {
  loading.value = true
  error.value = ''
  try {
    const planId = parseInt(route.params.id as string)
    plan.value = await subscriptionPlanService.getPlanDetails(planId)
    
    // Update page title
    if (plan.value) {
      document.title = `${plan.value.name} - Subscription Plan Details - Cash Pro`
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to load plan details'
  } finally {
    loading.value = false
  }
}

// Watch for route changes
watch(() => route.params.id, () => {
  fetchPlanDetails()
})

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

function handleEdit() {
  router.push(`/admin/subscriptions?edit=${plan.value?.id}`)
}

onMounted(() => {
  fetchPlanDetails()
})
</script>

<style scoped>
</style>

