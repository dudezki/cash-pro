import type { NavItem, NavigationConfig } from '../types/navigation'
import { useAuthStore } from '../stores/auth'

// Re-export types for use in other modules
export type { NavItem, NavigationConfig }

/**
 * Get navigation items for super admin
 */
export function getSuperAdminNavigation(): NavigationConfig {
  return {
    items: [
      {
        id: 'dashboard',
        label: 'Dashboard',
        icon: 'grid-outline',
        path: '/dashboard'
      },
      {
        id: 'admin',
        label: 'Administration',
        icon: 'settings-outline',
        children: [
          {
            id: 'admin-users',
            label: 'User Management',
            icon: 'people-outline',
            path: '/admin/users'
          },
          {
            id: 'admin-companies',
            label: 'Company Management',
            icon: 'business-outline',
            path: '/admin/companies'
          },
          {
            id: 'admin-subscriptions',
            label: 'Subscription Plans',
            icon: 'card-outline',
            path: '/admin/subscriptions'
          },
          {
            id: 'admin-system',
            label: 'System Settings',
            icon: 'construct-outline',
            path: '/admin/system'
          }
        ]
      },
      {
        id: 'monitoring',
        label: 'Monitoring',
        icon: 'stats-chart-outline',
        children: [
          {
            id: 'monitoring-logs',
            label: 'System Logs',
            icon: 'document-text-outline',
            path: '/admin/logs'
          },
          {
            id: 'monitoring-metrics',
            label: 'Metrics',
            icon: 'analytics-outline',
            path: '/admin/metrics'
          },
          {
            id: 'monitoring-health',
            label: 'Health Check',
            icon: 'medical-outline',
            path: '/admin/health'
          }
        ]
      },
      {
        id: 'settings',
        label: 'Settings',
        icon: 'lock-closed-outline',
        children: [
          {
            id: 'settings-roles',
            label: 'Roles',
            icon: 'person-outline',
            path: '/settings/roles'
          },
          {
            id: 'settings-permissions',
            label: 'Permissions',
            icon: 'key-outline',
            path: '/settings/permissions'
          }
        ]
      }
    ]
  }
}

/**
 * Get navigation items for regular users based on subscription and role
 */
export function getUserNavigation(
  subscriptionTier: string | null,
  userRole: string | null,
  hasCompany: boolean
): NavigationConfig {
  if (!hasCompany) {
    return {
      items: [
        {
          id: 'dashboard',
          label: 'Dashboard',
          icon: 'grid-outline',
          path: '/dashboard'
        }
      ]
    }
  }

  const baseItems: NavItem[] = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: 'grid-outline',
      path: '/dashboard'
    }
  ]

  // Financial Management (available for all tiers)
  const financialItems: NavItem[] = [
    {
      id: 'invoices',
      label: 'Invoices',
      icon: 'document-text-outline',
      path: '/invoices',
      requiresPermission: 'invoice:read'
    },
    {
      id: 'customers',
      label: 'Customers',
      icon: 'people-outline',
      path: '/customers',
      requiresPermission: 'customer:read'
    },
    {
      id: 'payments',
      label: 'Payments',
      icon: 'cash-outline',
      path: '/payments',
      requiresPermission: 'payment:read'
    }
  ]

  // Reports & Analytics (starter and above)
  const reportsItems: NavItem[] = [
    {
      id: 'reports',
      label: 'Reports',
      icon: 'document-attach-outline',
      path: '/reports',
      requiresSubscription: ['starter', 'professional', 'enterprise']
    },
    {
      id: 'analytics',
      label: 'Analytics',
      icon: 'stats-chart-outline',
      path: '/analytics',
      requiresSubscription: ['professional', 'enterprise']
    }
  ]

  // Advanced Features (professional and above)
  const advancedItems: NavItem[] = [
    {
      id: 'projects',
      label: 'Projects',
      icon: 'folder-outline',
      path: '/projects',
      requiresSubscription: ['professional', 'enterprise']
    },
    {
      id: 'expenses',
      label: 'Expenses',
      icon: 'wallet-outline',
      path: '/expenses',
      requiresSubscription: ['professional', 'enterprise']
    },
    {
      id: 'inventory',
      label: 'Inventory',
      icon: 'cube-outline',
      path: '/inventory',
      requiresSubscription: ['enterprise']
    }
  ]

  // Enterprise Features
  const enterpriseItems: NavItem[] = [
    {
      id: 'integrations',
      label: 'Integrations',
      icon: 'link-outline',
      path: '/integrations',
      requiresSubscription: ['enterprise']
    },
    {
      id: 'api-keys',
      label: 'API Keys',
      icon: 'key-outline',
      path: '/api-keys',
      requiresSubscription: ['enterprise'],
      requiresRole: ['owner', 'admin']
    }
  ]

  // Settings (role-based)
  const settingsItems: NavItem[] = [
    {
      id: 'settings-profile',
      label: 'Profile',
      icon: 'person-outline',
      path: '/settings/profile'
    },
    {
      id: 'settings-company',
      label: 'Company',
      icon: 'business-outline',
      path: '/settings/company',
      requiresRole: ['owner', 'admin']
    },
    {
      id: 'settings-billing',
      label: 'Billing',
      icon: 'card-outline',
      path: '/settings/billing',
      requiresRole: ['owner', 'admin']
    },
    {
      id: 'settings-roles',
      label: 'Roles & Permissions',
      icon: 'lock-closed-outline',
      path: '/settings/roles',
      requiresRole: ['owner', 'admin']
    }
  ]

  // Build navigation structure
  const navItems: NavItem[] = [...baseItems]

  // Add Financial Management section
  if (financialItems.length > 0) {
    navItems.push({
      id: 'financial',
      label: 'Financial',
      icon: 'briefcase-outline',
      children: financialItems
    })
  }

  // Add Reports section if subscription allows
  if (reportsItems.length > 0 && subscriptionTier && ['starter', 'professional', 'enterprise'].includes(subscriptionTier)) {
    navItems.push({
      id: 'reports-section',
      label: 'Reports',
      icon: 'bar-chart-outline',
      children: reportsItems
    })
  }

  // Add Advanced Features if subscription allows
  if (advancedItems.length > 0 && subscriptionTier && ['professional', 'enterprise'].includes(subscriptionTier)) {
    navItems.push({
      id: 'advanced',
      label: 'Advanced',
      icon: 'flash-outline',
      children: advancedItems
    })
  }

  // Add Enterprise Features if subscription allows
  if (enterpriseItems.length > 0 && subscriptionTier === 'enterprise') {
    navItems.push({
      id: 'enterprise',
      label: 'Enterprise',
      icon: 'rocket-outline',
      children: enterpriseItems
    })
  }

  // Add Settings section
  navItems.push({
    id: 'settings',
    label: 'Settings',
    icon: 'settings-outline',
    children: settingsItems
  })

  return {
    items: navItems
  }
}

/**
 * Filter navigation items based on user permissions and subscription
 */
export function filterNavigationByAccess(
  items: NavItem[],
  userRole: string | null,
  subscriptionTier: string | null,
  hasPermission: (permission: string) => boolean
): NavItem[] {
  return items
    .map(item => {
      // Check if item requires specific role
      if (item.requiresRole && userRole && !item.requiresRole.includes(userRole)) {
        return null
      }

      // Check if item requires specific subscription
      if (item.requiresSubscription && subscriptionTier && !item.requiresSubscription.includes(subscriptionTier)) {
        return null
      }

      // Check if item requires specific permission
      if (item.requiresPermission && !hasPermission(item.requiresPermission)) {
        return null
      }

      // Recursively filter children
      if (item.children) {
        const filteredChildren = filterNavigationByAccess(
          item.children,
          userRole,
          subscriptionTier,
          hasPermission
        )
        if (filteredChildren.length === 0 && !item.path) {
          return null // Hide parent if no children are visible
        }
        return {
          ...item,
          children: filteredChildren
        }
      }

      return item
    })
    .filter((item): item is NavItem => item !== null)
}

