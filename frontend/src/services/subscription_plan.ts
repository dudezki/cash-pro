import api from './api'

export interface Module {
  id: number
  name: string
  code: string
  description: string | null
  category: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface SubscriptionPlanModule {
  id: number
  plan_id: number
  module_id: number
  is_enabled: boolean
  module: Module
}

export interface SubscriptionPlan {
  id: number
  name: string
  tier: string
  description: string | null
  price_monthly: number
  price_annual: number
  currency: string
  is_active: boolean
  max_users: number | null
  max_storage_gb: number | null
  created_at: string
  updated_at: string
  modules: SubscriptionPlanModule[]
}

export interface SubscriptionPlanDetail extends SubscriptionPlan {
  total_subscribers: number
  active_subscribers: number
  trial_subscribers: number
  cancelled_subscribers: number
  expired_subscribers: number
  total_companies: number
  enabled_modules_count: number
}

export const subscriptionPlanService = {
  async getPlanDetails(planId: number): Promise<SubscriptionPlanDetail> {
    const response = await api.get<SubscriptionPlanDetail>(`/api/admin/plans/${planId}`)
    return response.data
  }
}

