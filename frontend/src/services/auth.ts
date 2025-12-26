import api from './api'

export interface RegisterData {
  email: string
  password: string
  first_name: string
  last_name: string
}

export interface LoginData {
  email_or_username: string
  password: string
}

export interface AuthResponse {
  person: {
    id: number
    email: string
    first_name: string | null
    last_name: string | null
    is_active: boolean
    is_verified: boolean
    is_super_admin: boolean
  }
  companies: Array<{
    id: number
    name: string
    slug: string
    database_name: string | null
  }>
  current_company_id: number | null
  is_impersonating: boolean
}

export const authService = {
  async register(data: RegisterData): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/api/auth/register', data)
    return response.data
  },

  async login(data: LoginData): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/api/auth/login', {
      email_or_username: data.email_or_username,
      password: data.password
    })
    return response.data
  },

  async logout(): Promise<void> {
    await api.post('/api/auth/logout')
  },

  async getCurrentUser(): Promise<AuthResponse> {
    const response = await api.get<AuthResponse>('/api/auth/me')
    return response.data
  },

  async switchCompany(companyId: number): Promise<void> {
    await api.post('/api/auth/switch-company', { company_id: companyId })
  }
}

