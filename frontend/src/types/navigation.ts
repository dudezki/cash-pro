export type NavItem = {
  id: string
  label: string
  icon?: string
  path?: string
  children?: NavItem[]
  requiresPermission?: string // e.g., "invoice:read", "customer:write"
  requiresRole?: string[] // e.g., ["owner", "admin"]
  requiresSubscription?: string[] // e.g., ["professional", "enterprise"]
  badge?: string | number
}

export type NavigationConfig = {
  items: NavItem[]
}
