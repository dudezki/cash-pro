import api from './api'

export interface Permission {
  id: number
  resource_type: string
  action: string
  description: string | null
}

export interface Role {
  id: number
  name: string
  description: string | null
  company_id: number
  permissions: Permission[]
}

export interface CreateRoleData {
  name: string
  description?: string
  permission_ids: number[]
}

export interface AssignRoleData {
  user_id: number
  role_id: number
}

export const rbacService = {
  async getRoles(): Promise<Role[]> {
    const response = await api.get<Role[]>('/api/rbac/roles')
    return response.data
  },

  async createRole(data: CreateRoleData): Promise<Role> {
    const response = await api.post<Role>('/api/rbac/roles', data)
    return response.data
  },

  async getPermissions(): Promise<Permission[]> {
    const response = await api.get<Permission[]>('/api/rbac/permissions')
    return response.data
  },

  async assignRole(data: AssignRoleData): Promise<void> {
    await api.post('/api/rbac/assign-role', data)
  }
}

