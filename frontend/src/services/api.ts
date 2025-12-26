import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized - redirect to login only if not already on login/register page
      // Import here to avoid circular dependency
      if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
        import('../stores/auth').then(({ useAuthStore }) => {
          const authStore = useAuthStore()
          authStore.logout()
          window.location.href = '/login'
        })
      }
    }
    return Promise.reject(error)
  }
)

export default api
export { api }

