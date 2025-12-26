<template>
  <nav v-if="items.length > 0" class="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
    <template v-for="(item, index) in items" :key="index">
      <router-link
        :to="item.to"
        class="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
        :class="{ 'text-gray-900 dark:text-gray-100 font-medium': index === items.length - 1 }"
      >
        {{ item.label }}
      </router-link>
      <span v-if="index < items.length - 1" class="text-gray-400 dark:text-gray-500">/</span>
    </template>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

interface BreadcrumbItem {
  label: string
  to: string
}

const props = defineProps<{
  items?: BreadcrumbItem[]
}>()

const route = useRoute()

const items = computed(() => {
  // Use provided items if available
  if (props.items && props.items.length > 0) {
    return props.items
  }
  
  // Use route meta breadcrumbs if available
  if (route.meta.breadcrumbs && Array.isArray(route.meta.breadcrumbs)) {
    return route.meta.breadcrumbs as BreadcrumbItem[]
  }
  
  // Auto-generate from route path
  const routeItems: BreadcrumbItem[] = []
  const pathSegments = route.path.split('/').filter(Boolean)
  
  let currentPath = ''
  pathSegments.forEach((segment) => {
    currentPath += `/${segment}`
    const label = segment
      .split('-')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
    
    routeItems.push({
      label,
      to: currentPath
    })
  })
  
  // Always add home if not already present
  if (routeItems.length > 0 && routeItems[0].label !== 'Home') {
    routeItems.unshift({ label: 'Home', to: '/dashboard' })
  }
  
  return routeItems
})
</script>

<style scoped>
</style>

