<script setup lang="ts">
import type { SeoResult } from '~/composables/useAnalyser'

const props = defineProps<{ data: SeoResult }>()

type Status = 'pass' | 'warn' | 'fail'

interface Check {
  label: string
  detail: string
  status: Status
}

const checks = computed<Check[]>(() => {
  const d = props.data
  return [
    {
      label: 'Title tag',
      status: !d.title ? 'fail' : d.title.length < 10 || d.title.length > 70 ? 'warn' : 'pass',
      detail: d.title ? `${d.title.length} characters` : 'Missing',
    },
    {
      label: 'Meta description',
      status: !d.description ? 'fail' : d.description.length < 50 || d.description.length > 160 ? 'warn' : 'pass',
      detail: d.description ? `${d.description.length} characters` : 'Missing',
    },
    {
      label: 'Canonical URL',
      status: d.canonical ? 'pass' : 'warn',
      detail: d.canonical ?? 'Not set',
    },
    {
      label: 'Robots meta',
      status: d.robots_meta ? 'pass' : 'warn',
      detail: d.robots_meta ?? 'Not set (defaults to index, follow)',
    },
    {
      label: 'robots.txt',
      status: d.robots_txt_found ? 'pass' : 'warn',
      detail: d.robots_txt_found ? 'Found' : 'Not found',
    },
    {
      label: 'Sitemap',
      status: d.sitemap_found ? 'pass' : 'warn',
      detail: d.sitemap_found ? 'Found at /sitemap.xml' : 'Not found at /sitemap.xml',
    },
    {
      label: 'Open Graph tags',
      status: Object.keys(d.og_tags).length >= 3 ? 'pass' : Object.keys(d.og_tags).length > 0 ? 'warn' : 'fail',
      detail: Object.keys(d.og_tags).length > 0 ? Object.keys(d.og_tags).join(', ') : 'None found',
    },
    {
      label: 'Structured data',
      status: d.structured_data.length > 0 ? 'pass' : 'warn',
      detail: d.structured_data.length > 0 ? `${d.structured_data.length} JSON-LD block(s)` : 'None found',
    },
  ]
})

const h1Count = computed(() => props.data.headings.h1?.length ?? 0)
const h1Status = computed<Status>(() => {
  if (h1Count.value === 0) return 'fail'
  if (h1Count.value > 1) return 'warn'
  return 'pass'
})

function statusColor(s: Status) {
  return s === 'pass' ? 'success' : s === 'warn' ? 'warning' : 'error'
}

function statusIcon(s: Status) {
  return s === 'pass' ? '✓' : s === 'warn' ? '!' : '✗'
}
</script>

<template>
  <UCard>
    <template #header>
      <div class="flex items-center gap-2">
        <UIcon name="i-heroicons-document-text" class="w-5 h-5 text-primary-500" />
        <h2 class="text-lg font-bold">SEO</h2>
      </div>
    </template>

    <div class="flex flex-col gap-6">
      <!-- Checks -->
      <div class="flex flex-col gap-2">
        <div
          v-for="check in checks"
          :key="check.label"
          class="flex items-center gap-3 bg-gray-50 rounded-lg px-3 py-2.5"
        >
          <UBadge :color="statusColor(check.status)" variant="subtle" size="sm" class="w-6 h-6 flex items-center justify-center rounded-full flex-shrink-0 font-bold text-xs">
            {{ statusIcon(check.status) }}
          </UBadge>
          <span class="text-sm font-medium w-44 flex-shrink-0">{{ check.label }}</span>
          <span class="text-xs text-gray-500 break-all">{{ check.detail }}</span>
        </div>
      </div>

      <!-- Heading structure -->
      <div class="flex flex-col gap-3">
        <div class="flex items-center gap-2">
          <p class="text-sm font-semibold text-gray-700">Heading structure</p>
          <UBadge :color="statusColor(h1Status)" variant="subtle" size="sm">H1: {{ h1Count }}</UBadge>
        </div>
        <div v-for="level in ['h1','h2','h3','h4','h5','h6']" :key="level">
          <div v-if="data.headings[level]?.length" class="flex gap-3 items-start mb-1.5">
            <span class="text-xs font-bold text-gray-400 bg-gray-100 rounded px-1.5 py-0.5 mt-0.5 min-w-[2rem] text-center flex-shrink-0">
              {{ level.toUpperCase() }}
            </span>
            <ul class="flex flex-col gap-1">
              <li v-for="text in data.headings[level]" :key="text" class="text-sm text-gray-700">{{ text }}</li>
            </ul>
          </div>
        </div>
        <p v-if="Object.keys(data.headings).length === 0" class="text-xs text-gray-400">No headings found.</p>
      </div>

      <!-- OG tags -->
      <div v-if="Object.keys(data.og_tags).length" class="flex flex-col gap-2">
        <p class="text-sm font-semibold text-gray-700">Open Graph tags</p>
        <table class="w-full text-sm border-collapse">
          <tbody>
            <tr v-for="(val, key) in data.og_tags" :key="key" class="border-b border-gray-100 last:border-0">
              <td class="py-1.5 pr-4 font-medium text-gray-500 whitespace-nowrap w-44 align-top">{{ key }}</td>
              <td class="py-1.5 text-gray-700 break-all">{{ val }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </UCard>
</template>
