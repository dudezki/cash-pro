<template>
  <div class="relative">
    <!-- Main Nav Item -->
    <router-link
      v-if="item.path"
      :to="item.path"
      class="flex items-center text-sm font-medium rounded-md transition-colors w-full relative z-10 cursor-pointer"
      :class="[
        level > 0 
          ? (isActive 
              ? 'text-indigo-600 dark:text-indigo-400 font-semibold' 
              : 'text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100')
          : (isActive 
              ? 'bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400' 
              : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-gray-100'),
        level > 0 ? 'pl-9 py-1.5' : 'px-3 py-2'
      ]"
    >
      <ion-icon
        v-if="item.icon"
        :name="item.icon"
        class="flex-shrink-0"
        style="width: 1.25rem; height: 1.25rem; font-size: 1.25rem;"
        :class="[
          level > 0
            ? (isActive ? 'text-indigo-600 dark:text-indigo-400' : 'text-gray-500 dark:text-gray-400')
            : (isActive ? 'text-indigo-600 dark:text-indigo-400' : 'text-gray-500 dark:text-gray-400'),
          level > 0 ? 'mr-2' : 'mr-3'
        ]"
      ></ion-icon>
      <span class="flex-1 min-w-0">{{ item.label }}</span>
      <span v-if="item.badge" class="ml-2 px-2 py-0.5 text-xs bg-indigo-100 dark:bg-indigo-900/50 text-indigo-600 dark:text-indigo-400 rounded-full">
        {{ item.badge }}
      </span>
    </router-link>

    <!-- Parent Nav Item (with children) -->
    <button
      v-else
      @click.stop="toggleExpanded"
      class="w-full flex items-center text-sm font-medium rounded-md transition-colors relative z-10"
      :class="[
        isActive 
          ? 'bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400' 
          : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-gray-100',
        level > 0 ? 'pl-9 py-1.5' : 'px-3 py-2'
      ]"
    >
      <ion-icon
        v-if="item.icon"
        :name="item.icon"
        class="flex-shrink-0 transition-transform duration-200"
        style="width: 1.25rem; height: 1.25rem; font-size: 1.25rem;"
        :class="[
          isActive ? 'text-indigo-600 dark:text-indigo-400' : 'text-gray-500 dark:text-gray-400',
          isExpanded ? 'rotate-90' : '',
          level > 0 ? 'mr-2' : 'mr-3'
        ]"
      ></ion-icon>
      <span class="flex-1 text-left min-w-0">{{ item.label }}</span>
      <span v-if="item.badge" class="ml-2 px-2 py-0.5 text-xs bg-indigo-100 dark:bg-indigo-900/50 text-indigo-600 dark:text-indigo-400 rounded-full flex-shrink-0">
        {{ item.badge }}
      </span>
      <ion-icon
        :name="isExpanded ? 'chevron-down' : 'chevron-forward'"
        class="ml-2 text-gray-400 dark:text-gray-500 flex-shrink-0 transition-transform duration-200"
        style="width: 1rem; height: 1rem; font-size: 1rem;"
      ></ion-icon>
    </button>

    <!-- Sub Navigation with Accordion Animation -->
    <transition
      name="accordion"
      @enter="onEnter"
      @after-enter="onAfterEnter"
      @leave="onLeave"
      @after-leave="onAfterLeave"
    >
      <div
        v-if="item.children && isExpanded"
        class="overflow-hidden w-full mt-1"
      >
        <div class="space-y-0.5 relative pl-4">
          <div class="absolute left-3 top-0 bottom-0 w-0.5 bg-gray-200 dark:bg-gray-700 pointer-events-none"></div>
          <NavItem
            v-for="child in item.children"
            :key="child.id"
            :item="child"
            :level="level + 1"
          />
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useNavigationStore } from '../../stores/navigation'
import { NavItem as NavItemType } from '../../types/navigation'

const props = defineProps<{
  item: NavItemType
  level: number
}>()

const navStore = useNavigationStore()

const isActive = computed(() => navStore.isItemActive(props.item))
const isExpanded = computed(() => navStore.isExpanded(props.item.id))

function toggleExpanded() {
  navStore.toggleExpanded(props.item.id)
}

// Accordion animation handlers
function onEnter(el: Element) {
  const element = el as HTMLElement
  const height = element.scrollHeight
  element.style.height = '0'
  element.style.opacity = '0'
  // Force reflow
  element.offsetHeight
  requestAnimationFrame(() => {
    element.style.height = `${height}px`
    element.style.opacity = '1'
  })
}

function onAfterEnter(el: Element) {
  const element = el as HTMLElement
  element.style.height = 'auto'
}

function onLeave(el: Element) {
  const element = el as HTMLElement
  const height = element.scrollHeight
  element.style.height = `${height}px`
  element.style.opacity = '1'
  // Force reflow
  element.offsetHeight
  requestAnimationFrame(() => {
    element.style.height = '0'
    element.style.opacity = '0'
  })
}

function onAfterLeave(el: Element) {
  const element = el as HTMLElement
  element.style.height = ''
  element.style.opacity = ''
}
</script>

<style scoped>
.accordion-enter-active {
  transition: height 0.3s ease, opacity 0.3s ease;
  overflow: hidden;
}

.accordion-leave-active {
  transition: height 0.3s ease, opacity 0.3s ease;
  overflow: hidden;
}

/* Ensure ion-icon doesn't break layout - scoped to this component */
:deep(ion-icon) {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
</style>

