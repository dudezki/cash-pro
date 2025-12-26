import api from './api'

export interface UserContext {
  subscription_tier: string | null
  role: string | null
  permissions: string[]
}

export async function getUserContext(companyId: number): Promise<UserContext> {
  try {
    // Fetch subscription
    const subscriptionRes = await api.get(`/subscriptions/current?company_id=${companyId}`)
    const subscription = subscriptionRes.data

    // Fetch user role in company
    const roleRes = await api.get(`/auth/me`)
    const userData = roleRes.data

    // Get role from person_company relationship
    // This would need to be added to the /auth/me endpoint or a new endpoint
    // For now, we'll use a mock approach
    
    // Fetch permissions from RBAC
    let permissions: string[] = []
    try {
      const permissionsRes = await api.get('/rbac/permissions')
      // This would need to be filtered by user's actual permissions
      // For now, we'll use a simplified approach
    } catch (e) {
      console.warn('Could not fetch permissions:', e)
    }

    return {
      subscription_tier: subscription?.plan_tier || null,
      role: userData.role || null, // This needs to be added to the API response
      permissions: permissions
    }
  } catch (error) {
    console.error('Error fetching user context:', error)
    return {
      subscription_tier: null,
      role: null,
      permissions: []
    }
  }
}

