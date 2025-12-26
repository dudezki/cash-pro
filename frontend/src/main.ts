import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { IonicVue } from '@ionic/vue'
import router from './router'
import './style.css'
import App from './App.vue'

// Import ionicons
import { addIcons } from 'ionicons'
import * as ionicons from 'ionicons/icons'

const app = createApp(App)
const pinia = createPinia()

// Add error handler
app.config.errorHandler = (err, instance, info) => {
  console.error('Vue error:', err, info)
  // Show error in console for debugging
}

// Add all ionicons to the icon registry
addIcons(ionicons)

app.use(pinia)
app.use(router)

// Initialize theme store to apply theme on app load
import('./stores/theme').then(({ useThemeStore }) => {
  useThemeStore() // This will initialize and apply the theme
})

// Mount app
app.mount('#app')
