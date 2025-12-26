import api from './api'

export interface User {
  id: number
  email: string
  username?: string | null
  first_name: string | null
  last_name: string | null
  is_active: boolean
  is_verified: boolean
  is_super_admin: boolean
  created_at: string
}

export interface CreateUserData {
  email: string
  password: string
  first_name?: string
  last_name?: string
  username?: string
  phone?: string
  is_active?: boolean
  is_verified?: boolean
  is_super_admin?: boolean
}

export interface Company {
  id: number
  name: string
  slug: string
  database_name: string | null
  created_at: string
  has_database: boolean
}

export const adminService = {
  async listUsers(): Promise<User[]> {
    const response = await api.get<User[]>('/api/admin/users')
    return response.data
  },

  async listCompanies(): Promise<Company[]> {
    const response = await api.get<Company[]>('/api/admin/companies')
    return response.data
  },

  async impersonateUser(userId: number): Promise<void> {
    await api.post(`/api/admin/impersonate/${userId}`)
  },

  async stopImpersonate(): Promise<void> {
    await api.post('/api/admin/stop-impersonate')
  },

  async createTenantDb(companyId: number): Promise<{ message: string; database_name: string }> {
    const response = await api.post<{ message: string; database_name: string }>(
      `/api/admin/companies/${companyId}/create-db`
    )
    return response.data
  },

  async createUser(userData: CreateUserData): Promise<User> {
    const response = await api.post<User>('/api/admin/users', userData)
    return response.data
  }
}

