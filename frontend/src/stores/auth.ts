import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { authService, type AuthResponse } from '../services/auth'

const STORAGE_KEY = 'cash_pro_auth'

interface StoredAuthState {
  person: AuthResponse['person'] | null
  companies: AuthResponse['companies']
  currentCompanyId: number | null
  isImpersonating: boolean
}

// Load initial state from localStorage
function loadStoredState(): StoredAuthState | null {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      return JSON.parse(stored)
    }
  } catch (e) {
    console.warn('Failed to load stored auth state:', e)
  }
  return null
}

// Save state to localStorage
function saveState(state: StoredAuthState) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
  } catch (e) {
    console.warn('Failed to save auth state:', e)
  }
}

// Clear stored state
function clearStoredState() {
  try {
    localStorage.removeItem(STORAGE_KEY)
  } catch (e) {
    console.warn('Failed to clear stored auth state:', e)
  }
}

export const useAuthStore = defineStore('auth', () => {
  // Initialize from localStorage if available
  const storedState = loadStoredState()
  
  const person = ref<AuthResponse['person'] | null>(storedState?.person || null)
  const companies = ref<AuthResponse['companies']>(storedState?.companies || [])
  const currentCompanyId = ref<number | null>(storedState?.currentCompanyId || null)
  const isImpersonating = ref(storedState?.isImpersonating || false)
  const isLoading = ref(false)
  
  // Persist state to localStorage whenever it changes
  // Use immediate: false to avoid saving on initial load
  watch([person, companies, currentCompanyId, isImpersonating], () => {
    // Only save if person is not null (user is logged in)
    if (person.value !== null) {
      saveState({
        person: person.value,
        companies: companies.value,
        currentCompanyId: currentCompanyId.value,
        isImpersonating: isImpersonating.value
      })
    }
  }, { deep: true, immediate: false })

  const isAuthenticated = computed(() => person.value !== null)
  const isSuperAdmin = computed(() => person.value?.is_super_admin ?? false)
  const currentCompany = computed(() => 
    companies.value.find(c => c.id === currentCompanyId.value)
  )

  async function login(emailOrUsername: string, password: string) {
    const response = await authService.login({ email_or_username: emailOrUsername, password })
    person.value = response.person
    companies.value = response.companies
    currentCompanyId.value = response.current_company_id
    isImpersonating.value = response.is_impersonating
  }

  async function register(data: {
    email: string
    password: string
    first_name: string
    last_name: string
  }) {
    const response = await authService.register(data)
    person.value = response.person
    companies.value = response.companies
    currentCompanyId.value = response.current_company_id
    isImpersonating.value = response.is_impersonating
    // Note: User will be redirected to organization setup if no companies
  }

  async function logout() {
    await authService.logout()
    person.value = null
    companies.value = []
    currentCompanyId.value = null
    isImpersonating.value = false
    clearStoredState()
  }

  async function fetchCurrentUser() {
    // Prevent multiple simultaneous calls
    if (isLoading.value) {
      return
    }
    
    isLoading.value = true
    try {
      const response = await authService.getCurrentUser()
      person.value = response.person
      companies.value = response.companies
      currentCompanyId.value = response.current_company_id
      isImpersonating.value = response.is_impersonating
      // State will be saved automatically by the watch
    } catch (error) {
      // Not authenticated - clear state and stored data
      person.value = null
      companies.value = []
      currentCompanyId.value = null
      isImpersonating.value = false
      clearStoredState()
    } finally {
      isLoading.value = false
    }
  }

  async function switchCompany(companyId: number) {
    await authService.switchCompany(companyId)
    currentCompanyId.value = companyId
    // Refresh user data
    await fetchCurrentUser()
  }

  return {
    person,
    companies,
    currentCompanyId,
    isImpersonating,
    isLoading,
    isAuthenticated,
    isSuperAdmin,
    currentCompany,
    login,
    register,
    logout,
    fetchCurrentUser,
    switchCompany
  }
})

