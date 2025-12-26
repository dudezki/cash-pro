import { defineStore } from 'pinia'
import { ref, onUnmounted } from 'vue'

const THEME_KEY = 'cash_pro_theme'

export const useThemeStore = defineStore('theme', () => {
  // Initialize from localStorage or system preference
  const getInitialTheme = (): boolean => {
    if (typeof window === 'undefined') return false
    try {
      const stored = localStorage.getItem(THEME_KEY)
      if (stored !== null) {
        return stored === 'dark'
      }
      // Check system preference
      return window.matchMedia('(prefers-color-scheme: dark)').matches
    } catch (e) {
      return false
    }
  }

  const isDark = ref(getInitialTheme())

  // Apply theme to document
  const applyTheme = (dark: boolean) => {
    if (typeof document === 'undefined') return
    if (dark) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
    try {
      localStorage.setItem(THEME_KEY, dark ? 'dark' : 'light')
    } catch (e) {
      console.warn('Failed to save theme preference:', e)
    }
  }

  // Toggle theme
  function toggleTheme() {
    isDark.value = !isDark.value
    applyTheme(isDark.value)
  }

  // Set theme explicitly
  function setTheme(dark: boolean) {
    isDark.value = dark
    applyTheme(dark)
  }

  // Initialize theme on store creation
  if (typeof window !== 'undefined') {
    applyTheme(isDark.value)
  }

  return {
    isDark,
    toggleTheme,
    setTheme
  }
})

