<script setup lang="ts">
import type { TechResult } from '~/composables/useAnalyser'

const props = defineProps<{ data: TechResult }>()

const categoryOrder = [
  'CMS',
  'E-commerce',
  'JavaScript Framework',
  'JavaScript Library',
  'Static Site Generator',
  'UI Framework',
  'Analytics',
  'CDN',
  'Hosting',
  'Web Server',
  'Programming Language',
  'Font Service',
]

const sortedCategories = computed(() => {
  const keys = Object.keys(props.data.categories)
  return [
    ...categoryOrder.filter(c => keys.includes(c)),
    ...keys.filter(c => !categoryOrder.includes(c)),
  ]
})

function techsForCategory(cat: string) {
  return props.data.technologies.filter(t => t.category === cat)
}
</script>

<template>
  <UCard>
    <template #header>
      <div class="flex items-center gap-2">
        <UIcon name="i-heroicons-wrench-screwdriver" class="w-5 h-5 text-primary-500" />
        <h2 class="text-lg font-bold">Technology Detection</h2>
      </div>
    </template>

    <div class="flex flex-col gap-6">
      <div v-if="data.technologies.length === 0" class="text-sm text-gray-400 py-4">
        No technologies detected — the page may be static or heavily obfuscated.
      </div>

      <template v-else>
        <div class="flex items-baseline gap-2">
          <span class="text-3xl font-bold text-primary-600">{{ data.technologies.length }}</span>
          <span class="text-sm text-gray-400">technologies detected across {{ sortedCategories.length }} categories</span>
        </div>

        <div v-for="cat in sortedCategories" :key="cat" class="flex flex-col gap-2">
          <p class="text-xs font-bold uppercase tracking-wider text-gray-400">{{ cat }}</p>
          <div class="flex flex-wrap gap-2">
            <div
              v-for="tech in techsForCategory(cat)"
              :key="tech.name"
              class="flex items-center gap-2 bg-primary-50 border border-primary-100 rounded-lg px-3 py-2"
            >
              <span class="text-base leading-none">{{ tech.icon ?? '📦' }}</span>
              <div class="flex flex-col gap-0.5">
                <span class="text-sm font-semibold text-primary-800">{{ tech.name }}</span>
                <span v-if="tech.version" class="text-xs text-primary-400">v{{ tech.version }}</span>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>
  </UCard>
</template>
