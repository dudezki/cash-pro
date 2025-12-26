<template>
  <div class="h-screen flex bg-gray-50 dark:bg-gray-900">
    <!-- Side Navigation (Full Height) -->
    <aside class="w-56 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex-shrink-0 h-full">
      <SideNavigation />
    </aside>

    <!-- Right Side Content Area -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Top Header Bar -->
      <header class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 h-14 flex-shrink-0">
        <div class="h-full flex items-center px-4">
          <!-- Brand -->
          <div class="flex-shrink-0">
            <router-link to="/dashboard" class="text-lg font-bold text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300">
              Cash Pro
            </router-link>
          </div>
          
          <!-- Top Header (Page Title) -->
          <div class="flex-1 flex items-center justify-center">
            <h1 class="text-sm font-semibold text-gray-900 dark:text-gray-100">{{ pageTitle }}</h1>
          </div>
          
          <!-- Tools -->
          <div class="flex-shrink-0 flex items-center justify-end space-x-3">
            <div v-if="authStore.isImpersonating" class="bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 px-2 py-1 rounded text-xs font-medium">
              Impersonating
            </div>
            <select
              v-if="authStore.companies.length > 1"
              :value="authStore.currentCompanyId"
              @change="handleCompanySwitch"
              class="text-xs border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200 rounded px-2 py-1 focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option
                v-for="company in authStore.companies"
                :key="company.id"
                :value="company.id"
              >
                {{ company.name }}
              </option>
            </select>
            <button
              @click="themeStore.toggleTheme()"
              class="p-2 rounded-md text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              :title="themeStore.isDark ? 'Switch to light mode' : 'Switch to dark mode'"
            >
              <span v-if="themeStore.isDark">☀️</span>
              <span v-else>🌙</span>
            </button>
          </div>
        </div>
      </header>

      <!-- Breadcrumbs Row -->
      <div class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-3 flex items-center justify-between flex-shrink-0">
        <Breadcrumb :items="breadcrumbItems" />
        <div class="flex items-center space-x-2">
          <slot name="actions"></slot>
        </div>
      </div>

      <!-- Main Content Container -->
      <main class="flex-1 overflow-y-auto bg-gray-50 dark:bg-gray-900">
        <div
          v-motion
          :initial="{ opacity: 0, y: 10 }"
          :enter="{ opacity: 1, y: 0, transition: { duration: 0.3, ease: 'easeOut' } }"
          class="h-full p-4"
        >
          <slot />
        </div>
      </main>

      <!-- Footer -->
      <footer class="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 h-10 flex-shrink-0">
        <div class="h-full flex items-center justify-end px-4">
          <div class="text-xs text-gray-500 dark:text-gray-400">
            © {{ currentYear }} Cash Pro
          </div>
        </div>
      </footer>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useNavigationStore } from '../../stores/navigation'
import { useThemeStore } from '../../stores/theme'
import Breadcrumb from '../common/Breadcrumb.vue'
import SideNavigation from '../navigation/SideNavigation.vue'

const authStore = useAuthStore()
const navStore = useNavigationStore()
const themeStore = useThemeStore()
const route = useRoute()
const router = useRouter()

const currentYear = new Date().getFullYear()

onMounted(() => {
  // Load user context for navigation
  loadUserContext()
})

// Watch for route changes to auto-expand active items and update navigation
watch(() => route.path, () => {
  navStore.autoExpandActive()
  // Force navigation store to recompute active state
  if (navStore.navigation.items) {
    // Trigger reactivity by accessing the navigation
    const _ = navStore.navigation
  }
}, { immediate: true })

// Load user context (subscription, role, permissions)
async function loadUserContext() {
  if (authStore.isSuperAdmin) {
    // Super admin doesn't need subscription/role context
    return
  }

  if (!authStore.currentCompanyId) {
    return
  }

  // TODO: Fetch subscription and role from API
  // This should fetch:
  // - Current subscription tier from /api/subscriptions/current
  // - User's role in the company from /api/auth/me (needs to be added to response)
  // - User's permissions from /api/rbac/user-permissions (needs to be created)
  
  // For now, using mock data based on common scenarios
  // Replace with actual API calls when endpoints are available
  
  // Mock: Try to infer role from company relationship
  // In real implementation, this would come from PersonCompany.role
  const mockRole = 'admin' // owner, admin, member, or viewer
  
  // Mock: Subscription tier - would come from active subscription
  const mockSubscriptionTier = 'professional' // trial, starter, professional, enterprise
  
  // Mock: Permissions based on role
  // In real implementation, these would come from RBAC system
  const mockPermissions: string[] = []
  if (mockRole === 'owner' || mockRole === 'admin') {
    mockPermissions.push(
      'invoice:read', 'invoice:write', 'invoice:delete',
      'customer:read', 'customer:write', 'customer:delete',
      'payment:read', 'payment:write'
    )
  } else if (mockRole === 'member') {
    mockPermissions.push(
      'invoice:read', 'invoice:write',
      'customer:read', 'customer:write',
      'payment:read'
    )
  } else if (mockRole === 'viewer') {
    mockPermissions.push(
      'invoice:read',
      'customer:read',
      'payment:read'
    )
  }
  
  navStore.setUserContext(
    mockSubscriptionTier,
    mockRole,
    mockPermissions
  )
}

const pageTitle = computed(() => {
  return route.meta.title?.toString().replace(' - Cash Pro', '') || 'Dashboard'
})

const breadcrumbItems = computed(() => {
  // Custom breadcrumbs can be passed via route meta
  if (route.meta.breadcrumbs) {
    return route.meta.breadcrumbs as Array<{ label: string; to: string }>
  }
  return []
})

async function handleCompanySwitch(event: Event) {
  const target = event.target as HTMLSelectElement
  const companyId = parseInt(target.value)
  await authStore.switchCompany(companyId)
  // Reload user context after company switch
  loadUserContext()
}
</script>

<style scoped>
/* Smooth scrolling */
.overflow-y-auto {
  scrollbar-width: thin;
  scrollbar-color: #cbd5e0 #f7fafc;
}

.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f7fafc;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background-color: #cbd5e0;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background-color: #a0aec0;
}
</style>
