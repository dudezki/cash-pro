import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/LoginPage.vue'),
      meta: { 
        requiresAuth: false,
        title: 'Login - Cash Pro',
        description: 'Login to your Cash Pro account'
      }
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('../views/RegisterPage.vue'),
      meta: { 
        requiresAuth: false,
        title: 'Register - Cash Pro',
        description: 'Create a new Cash Pro account'
      }
    },
    {
      path: '/setup/organization',
      name: 'SetupOrganization',
      component: () => import('../views/SetupOrganizationPage.vue'),
      meta: { 
        requiresAuth: true,
        title: 'Create Organization - Cash Pro',
        description: 'Create your organization',
        breadcrumbs: [
          { label: 'Home', to: '/dashboard' },
          { label: 'Setup', to: '/setup/organization' },
          { label: 'Organization', to: '/setup/organization' }
        ]
      }
    },
    {
      path: '/setup/subscription',
      name: 'SetupSubscription',
      component: () => import('../views/SetupSubscriptionPage.vue'),
      meta: { 
        requiresAuth: true,
        title: 'Select Subscription - Cash Pro',
        description: 'Choose your subscription plan',
        breadcrumbs: [
          { label: 'Home', to: '/dashboard' },
          { label: 'Setup', to: '/setup/subscription' },
          { label: 'Subscription', to: '/setup/subscription' }
        ]
      }
    },
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: () => import('../views/DashboardPage.vue'),
      meta: { 
        requiresAuth: true,
        title: 'Dashboard - Cash Pro',
        description: 'Your Cash Pro dashboard',
        breadcrumbs: [
          { label: 'Home', to: '/dashboard' }
        ]
      }
    },
    {
      path: '/admin/users',
      name: 'AdminUsers',
      component: () => import('../views/AdminUsersPage.vue'),
      meta: { 
        requiresAuth: true, 
        requiresSuperAdmin: true,
        title: 'User Management - Cash Pro',
        description: 'Manage users and access',
        breadcrumbs: [
          { label: 'Home', to: '/dashboard' },
          { label: 'Admin', to: '/admin/users' },
          { label: 'Users', to: '/admin/users' }
        ]
      }
    },
    {
      path: '/admin/companies',
      name: 'AdminCompanies',
      component: () => import('../views/AdminCompaniesPage.vue'),
      meta: { 
        requiresAuth: true, 
        requiresSuperAdmin: true,
        title: 'Company Management - Cash Pro',
        description: 'Manage companies and tenant databases',
        breadcrumbs: [
          { label: 'Home', to: '/dashboard' },
          { label: 'Admin', to: '/admin/companies' },
          { label: 'Companies', to: '/admin/companies' }
        ]
      }
    },
    {
      path: '/admin/subscriptions',
      name: 'AdminSubscriptions',
      component: () => import('../views/AdminSubscriptionsPage.vue'),
      meta: { 
        requiresAuth: true, 
        requiresSuperAdmin: true,
        title: 'Subscription Plans - Cash Pro',
        description: 'Manage subscription plans and modules',
        breadcrumbs: [
          { label: 'Home', to: '/dashboard' },
          { label: 'Admin', to: '/admin/subscriptions' },
          { label: 'Subscriptions', to: '/admin/subscriptions' }
        ]
      }
    },
    {
      path: '/admin/subscriptions/:id',
      name: 'SubscriptionPlanDetails',
      component: () => import('../views/SubscriptionPlanDetailsPage.vue'),
      meta: { 
        requiresAuth: true, 
        requiresSuperAdmin: true,
        title: 'Subscription Plan Details - Cash Pro',
        description: 'View subscription plan details and statistics',
        breadcrumbs: [
          { label: 'Home', to: '/dashboard' },
          { label: 'Admin', to: '/admin/subscriptions' },
          { label: 'Subscriptions', to: '/admin/subscriptions' }
        ]
      }
    },
    {
      path: '/settings/roles',
      name: 'Roles',
      component: () => import('../views/RolesPage.vue'),
      meta: { 
        requiresAuth: true,
        title: 'Roles - Cash Pro',
        description: 'Manage roles and permissions',
        breadcrumbs: [
          { label: 'Home', to: '/dashboard' },
          { label: 'Settings', to: '/settings/roles' },
          { label: 'Roles', to: '/settings/roles' }
        ]
      }
    },
    {
      path: '/settings/permissions',
      name: 'Permissions',
      component: () => import('../views/PermissionsPage.vue'),
      meta: { 
        requiresAuth: true,
        title: 'Permissions - Cash Pro',
        description: 'View and manage permissions',
        breadcrumbs: [
          { label: 'Home', to: '/dashboard' },
          { label: 'Settings', to: '/settings/permissions' },
          { label: 'Permissions', to: '/settings/permissions' }
        ]
      }
    },
    {
      path: '/',
      redirect: '/dashboard'
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('../views/NotFoundPage.vue'),
      meta: {
        requiresAuth: false,
        title: '404 - Page Not Found - Cash Pro',
        description: 'The requested page could not be found'
      }
    }
  ]
})

router.beforeEach(async (to, from, next) => {
  try {
    const authStore = useAuthStore()
    
    // Update page title and meta tags
    if (to.meta.title) {
      document.title = to.meta.title as string
    }
    
    // Update meta description
    let metaDescription = document.querySelector('meta[name="description"]')
    if (!metaDescription) {
      metaDescription = document.createElement('meta')
      metaDescription.setAttribute('name', 'description')
      document.head.appendChild(metaDescription)
    }
    if (to.meta.description) {
      metaDescription.setAttribute('content', to.meta.description as string)
    }
    
    // Only fetch user if not already loading and not on public pages
    if (!authStore.isLoading && to.path !== '/login' && to.path !== '/register') {
      // If not authenticated, try to fetch user (in case session cookie exists)
      if (!authStore.isAuthenticated) {
        try {
          await authStore.fetchCurrentUser()
        } catch (error) {
          // Silently fail - user is not authenticated
        }
      }
    }
    
    // Check authentication requirements
    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
      next('/login')
      return
    }
    
    // Check super admin requirements
    if (to.meta.requiresSuperAdmin && !authStore.isSuperAdmin) {
      next('/dashboard')
      return
    }
    
    // Redirect authenticated users away from login/register pages
    if ((to.path === '/login' || to.path === '/register') && authStore.isAuthenticated) {
      // Super admins don't need companies - go to dashboard
      if (authStore.isSuperAdmin) {
        next('/dashboard')
        return
      }
      // Regular users without companies need to set up organization
      if (authStore.companies.length === 0) {
        next('/setup/organization')
        return
      }
      // Regular users with companies go to dashboard
      next('/dashboard')
      return
    }
    
    // Redirect regular users without companies to setup (unless already on setup pages)
    if (authStore.isAuthenticated && authStore.companies.length === 0 && !authStore.isSuperAdmin) {
      if (to.path !== '/setup/organization' && to.path !== '/setup/subscription') {
        next('/setup/organization')
        return
      }
    }
    
    // Allow navigation
    next()
  } catch (error) {
    console.error('Router guard error:', error)
    // On error, allow navigation to prevent blocking
    next()
  }
})

export default router

