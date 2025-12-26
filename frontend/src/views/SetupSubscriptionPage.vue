<template>
  <AuthenticatedLayout>
    <div class="max-w-4xl mx-auto px-4 py-6">
      <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-8">
        <h1 class="text-3xl font-bold text-center mb-6 text-gray-900 dark:text-gray-100">Choose Your Plan</h1>
        <p class="text-center text-gray-600 dark:text-gray-400 mb-8">
          Select a subscription plan for your organization
        </p>
        
        <div v-if="loading" class="text-center py-8">Loading plans...</div>
        <div v-else-if="error" class="text-red-600 text-sm bg-red-50 p-3 rounded mb-4">{{ error }}</div>
        
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div
            v-for="plan in plans"
            :key="plan.id"
            @click="selectPlan(plan)"
            :class="[
              'border-2 rounded-lg p-6 cursor-pointer transition-all',
              selectedPlan?.id === plan.id
                ? 'border-indigo-600 bg-indigo-50'
                : 'border-gray-200 hover:border-indigo-300'
            ]"
          >
            <h3 class="text-xl font-bold mb-2">{{ plan.name }}</h3>
            <div class="text-3xl font-bold text-indigo-600 mb-4">
              ${{ plan.price }}
              <span class="text-sm text-gray-500 font-normal">/month</span>
            </div>
            <ul class="space-y-2 mb-4">
              <li
                v-for="feature in plan.features"
                :key="feature"
                class="text-sm text-gray-600 flex items-start"
              >
                <span class="text-green-500 mr-2">✓</span>
                {{ feature }}
              </li>
            </ul>
            <button
              :class="[
                'w-full py-2 px-4 rounded-md font-medium transition-colors',
                selectedPlan?.id === plan.id
                  ? 'bg-indigo-600 text-white hover:bg-indigo-700'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              ]"
            >
              {{ selectedPlan?.id === plan.id ? 'Selected' : 'Select Plan' }}
            </button>
          </div>
        </div>
        
        <div v-if="selectedPlan" class="mt-8 flex justify-center">
          <button
            @click="handleSubscribe"
            :disabled="subscribing"
            class="bg-indigo-600 text-white py-3 px-8 rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-lg font-medium"
          >
            {{ subscribing ? 'Processing...' : 'Subscribe & Continue' }}
          </button>
        </div>
      </div>
    </div>
  </AuthenticatedLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { subscriptionService, type SubscriptionPlan } from '../services/subscription'
import { useAuthStore } from '../stores/auth'
import AuthenticatedLayout from '../components/layouts/AuthenticatedLayout.vue'

const router = useRouter()
const authStore = useAuthStore()

const plans = ref<SubscriptionPlan[]>([])
const selectedPlan = ref<SubscriptionPlan | null>(null)
const loading = ref(true)
const subscribing = ref(false)
const error = ref('')

async function fetchPlans() {
  loading.value = true
  error.value = ''
  try {
    const response = await subscriptionService.getAvailablePlans()
    plans.value = response.plans
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to load plans'
  } finally {
    loading.value = false
  }
}

function selectPlan(plan: SubscriptionPlan) {
  selectedPlan.value = plan
}

async function handleSubscribe() {
  if (!selectedPlan.value) return
  
  subscribing.value = true
  error.value = ''
  
  try {
    await subscriptionService.createSubscription({
      plan_name: selectedPlan.value.name,
      plan_tier: selectedPlan.value.tier,
      billing_cycle: selectedPlan.value.billing_cycle as 'monthly' | 'annual',
      price: selectedPlan.value.price,
      currency: selectedPlan.value.currency
    })
    
    // Refresh auth to get updated company with database
    await authStore.fetchCurrentUser()
    
    // Redirect to dashboard
    router.push('/dashboard')
  } catch (err: any) {
    console.error('Subscription error:', err)
    error.value = err.response?.data?.detail || 'Failed to create subscription. Please try again.'
  } finally {
    subscribing.value = false
  }
}

onMounted(() => {
  fetchPlans()
})
</script>

<style scoped>
</style>

