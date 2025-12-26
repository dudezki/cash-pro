<template>
  <div class="h-full flex flex-col navigation-container">
    <!-- Navigation Content (Full height minus user footer) -->
    <nav class="flex-1 overflow-y-auto min-h-0">
      <div v-if="navigation.items && navigation.items.length > 0" class="p-3 space-y-1">
        <NavItem
          v-for="item in navigation.items"
          :key="item.id"
          :item="item"
          :level="0"
        />
      </div>
      <div v-else class="p-3 text-xs text-gray-400 dark:text-gray-500 text-center">
        Loading navigation...
      </div>
    </nav>

    <!-- User Info Footer -->
    <div class="border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 flex-shrink-0">
      <div class="p-3">
        <div class="flex items-center space-x-2 mb-2">
          <div class="w-8 h-8 rounded-full bg-indigo-100 dark:bg-indigo-900/50 flex items-center justify-center flex-shrink-0">
            <span class="text-xs font-medium text-indigo-600 dark:text-indigo-400">
              {{ userInitials }}
            </span>
          </div>
          <div class="flex-1 min-w-0">
            <div class="text-xs font-medium text-gray-900 dark:text-gray-100 truncate">
              {{ authStore.person?.first_name }} {{ authStore.person?.last_name }}
            </div>
            <div class="text-xs text-gray-500 dark:text-gray-400 truncate">
              {{ authStore.person?.email }}
            </div>
          </div>
        </div>
        <div class="flex items-center justify-between">
          <div v-if="authStore.isSuperAdmin" class="px-2 py-0.5 bg-indigo-100 dark:bg-indigo-900/50 text-indigo-700 dark:text-indigo-300 rounded text-xs font-medium">
            Super Admin
          </div>
          <div v-else-if="authStore.currentCompany" class="text-xs text-gray-500 dark:text-gray-400 truncate flex-1">
            {{ authStore.currentCompany.name }}
          </div>
          <div v-else class="text-xs text-gray-400 dark:text-gray-500">
            No company
          </div>
          <div class="relative user-menu-container">
            <button
              @click.stop="showUserMenu = !showUserMenu"
              class="text-xs text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 px-2 py-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              ⋮
            </button>
            <div
              v-if="showUserMenu"
              class="absolute bottom-full right-0 mb-2 w-32 bg-white dark:bg-gray-800 rounded-md shadow-lg border border-gray-200 dark:border-gray-700 py-1 z-20"
              @click.stop
            >
              <button
                @click="handleLogout"
                class="w-full text-left px-3 py-2 text-xs text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNavigationStore } from '../../stores/navigation'
import { useAuthStore } from '../../stores/auth'
import NavItem from './NavItem.vue'

const navStore = useNavigationStore()
const authStore = useAuthStore()
const router = useRouter()

const showUserMenu = ref(false)

const navigation = computed(() => navStore.navigation)

const userInitials = computed(() => {
  const firstName = authStore.person?.first_name || ''
  const lastName = authStore.person?.last_name || ''
  return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase() || 'U'
})

// Close user menu when clicking outside
function handleClickOutside(event: MouseEvent) {
  const target = event.target as HTMLElement
  if (!target.closest('.user-menu-container')) {
    showUserMenu.value = false
  }
}

onMounted(() => {
  navStore.autoExpandActive()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

async function handleLogout() {
  showUserMenu.value = false
  await authStore.logout()
  router.push('/login')
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

