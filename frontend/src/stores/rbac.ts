import { defineStore } from 'pinia'
import { ref } from 'vue'
import { rbacService, type Role, type Permission } from '../services/rbac'

export const useRbacStore = defineStore('rbac', () => {
  const roles = ref<Role[]>([])
  const permissions = ref<Permission[]>([])

  async function fetchRoles() {
    roles.value = await rbacService.getRoles()
  }

  async function fetchPermissions() {
    permissions.value = await rbacService.getPermissions()
  }

  async function createRole(data: {
    name: string
    description?: string
    permission_ids: number[]
  }) {
    const role = await rbacService.createRole(data)
    roles.value.push(role)
    return role
  }

  async function assignRole(userId: number, roleId: number) {
    await rbacService.assignRole({ user_id: userId, role_id: roleId })
  }

  return {
    roles,
    permissions,
    fetchRoles,
    fetchPermissions,
    createRole,
    assignRole
  }
})

