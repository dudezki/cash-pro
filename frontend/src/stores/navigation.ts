import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useAuthStore } from './auth'
import { getSuperAdminNavigation, getUserNavigation, filterNavigationByAccess } from '../services/navigation'
import type { NavItem } from '../types/navigation'
import { useRouter } from 'vue-router'

export const useNavigationStore = defineStore('navigation', () => {
  const authStore = useAuthStore()
  const router = useRouter()
  
  // Get current route path safely
  const getCurrentPath = () => {
    try {
      return router.currentRoute.value.path
    } catch (e) {
      return '/'
    }
  }
  
  // User context (will be fetched from API)
  const subscriptionTier = ref<string | null>(null)
  const userRole = ref<string | null>(null)
  const userPermissions = ref<string[]>([])

  // Navigation state
  const expandedItems = ref<Set<string>>(new Set())

  // Get navigation based on user type
  // Computed properties are automatically reactive to their dependencies
  const navigation = computed(() => {
    // Check if user is authenticated first
    if (!authStore.isAuthenticated) {
      return { items: [] }
    }
    
    // For super admin, return all items
    if (authStore.isSuperAdmin) {
      return getSuperAdminNavigation()
    }
    
    // For regular users
    return getUserNavigation(
      subscriptionTier.value,
      userRole.value,
      authStore.companies.length > 0
    )
  })

  // Filter navigation by access
  const filteredNavigation = computed(() => {
    const nav = navigation.value
    
    // If no items, return empty
    if (!nav.items || nav.items.length === 0) {
      return { items: [] }
    }
    
    // For super admin, return all items
    if (authStore.isSuperAdmin) {
      return nav
    }

    // For regular users, filter by permissions and subscription
    return {
      items: filterNavigationByAccess(
        nav.items,
        userRole.value,
        subscriptionTier.value,
        (permission: string) => userPermissions.value.includes(permission)
      )
    }
  })

  // Check if item is active
  function isItemActive(item: NavItem): boolean {
    try {
      const currentPath = getCurrentPath()
      if (item.path) {
        // Exact match or starts with path (for nested routes)
        const normalizedPath = item.path.replace(/\/$/, '') // Remove trailing slash
        const normalizedCurrent = currentPath.replace(/\/$/, '')
        return normalizedCurrent === normalizedPath || normalizedCurrent.startsWith(normalizedPath + '/')
      }
      if (item.children) {
        return item.children.some(child => isItemActive(child))
      }
    } catch (e) {
      // Route might not be available during initialization
      return false
    }
    return false
  }

  // Toggle expanded state
  function toggleExpanded(itemId: string) {
    if (expandedItems.value.has(itemId)) {
      expandedItems.value.delete(itemId)
    } else {
      expandedItems.value.add(itemId)
    }
  }

  // Check if item is expanded
  function isExpanded(itemId: string): boolean {
    return expandedItems.value.has(itemId)
  }

  // Auto-expand active items
  function autoExpandActive() {
    const checkAndExpand = (items: NavItem[]) => {
      items.forEach(item => {
        if (isItemActive(item)) {
          if (item.children) {
            expandedItems.value.add(item.id)
            checkAndExpand(item.children)
          }
        } else if (item.children) {
          checkAndExpand(item.children)
        }
      })
    }
    checkAndExpand(filteredNavigation.value.items)
  }

  // Set user context
  function setUserContext(
    tier: string | null,
    role: string | null,
    permissions: string[]
  ) {
    subscriptionTier.value = tier
    userRole.value = role
    userPermissions.value = permissions
    // Auto-expand active items when context changes
    autoExpandActive()
  }

  return {
    navigation: filteredNavigation,
    subscriptionTier,
    userRole,
    userPermissions,
    expandedItems,
    isItemActive,
    toggleExpanded,
    isExpanded,
    autoExpandActive,
    setUserContext
  }
})

