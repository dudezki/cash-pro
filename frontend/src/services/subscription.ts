import api from './api'

export interface SubscriptionPlan {
  id: string
  name: string
  tier: string
  billing_cycle: string
  price: number
  currency: string
  features: string[]
}

export interface CreateSubscriptionData {
  plan_name: string
  plan_tier: string
  billing_cycle: 'monthly' | 'annual'
  price: number
  currency?: string
}

export interface Subscription {
  id: number
  company_id: number
  plan_name: string
  plan_tier: string
  status: string
  billing_cycle: string
  price: number
  currency: string
  starts_at: string
  ends_at: string | null
}

export const subscriptionService = {
  async getAvailablePlans(): Promise<{ plans: SubscriptionPlan[] }> {
    const response = await api.get<{ plans: SubscriptionPlan[] }>('/api/subscription/plans')
    return response.data
  },

  async createSubscription(data: CreateSubscriptionData): Promise<Subscription> {
    const response = await api.post<Subscription>('/api/subscription', data)
    return response.data
  }
}

