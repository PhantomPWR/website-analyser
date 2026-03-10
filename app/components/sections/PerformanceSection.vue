<script setup lang="ts">
import type { PerformanceResult, WebVital } from '~/composables/useAnalyser'

const props = defineProps<{ data: PerformanceResult }>()

type Status = 'pass' | 'warn' | 'fail'

function vitalStatus(score: number | null): Status {
  if (score === null) return 'warn'
  if (score >= 0.9) return 'pass'
  if (score >= 0.5) return 'warn'
  return 'fail'
}

function perfScoreStatus(score: number | null): Status {
  if (score === null) return 'warn'
  if (score >= 90) return 'pass'
  if (score >= 50) return 'warn'
  return 'fail'
}

function ringClass(s: Status) {
  return s === 'pass' ? 'border-green-500' : s === 'warn' ? 'border-amber-500' : 'border-red-500'
}

interface VitalRow {
  key: string
  label: string
  vital: WebVital
  hint: string
}

const vitals = computed<VitalRow[]>(() => [
  { key: 'fcp', label: 'First Contentful Paint', vital: props.data.fcp, hint: 'Good < 1.8s' },
  { key: 'lcp', label: 'Largest Contentful Paint', vital: props.data.lcp, hint: 'Good < 2.5s' },
  { key: 'cls', label: 'Cumulative Layout Shift', vital: props.data.cls, hint: 'Good < 0.1' },
  { key: 'ttfb', label: 'Time to First Byte', vital: props.data.ttfb, hint: 'Good < 800ms' },
  { key: 'inp', label: 'Interaction to Next Paint', vital: props.data.inp, hint: 'Good < 200ms' },
  { key: 'speed_index', label: 'Speed Index', vital: props.data.speed_index, hint: 'Good < 3.4s' },
])

function vitalBorderClass(s: Status) {
  return s === 'pass' ? 'border-green-500 bg-green-50' : s === 'warn' ? 'border-amber-500 bg-amber-50' : 'border-red-500 bg-red-50'
}

const overallStatus = computed(() => perfScoreStatus(props.data.performance_score))
</script>

<template>
  <UCard>
    <template #header>
      <div class="flex items-center gap-2">
        <UIcon name="i-heroicons-bolt" class="w-5 h-5 text-primary-500" />
        <h2 class="text-lg font-bold">Performance</h2>
      </div>
    </template>

    <div class="flex flex-col gap-6">
      <!-- Score or info banner -->
      <div v-if="data.pagespeed_available" class="flex items-center gap-5">
        <div
          class="w-20 h-20 rounded-full border-[5px] flex flex-col items-center justify-center flex-shrink-0"
          :class="ringClass(overallStatus)"
        >
          <span class="text-xl font-bold leading-none">{{ data.performance_score ?? '—' }}</span>
          <span class="text-xs text-gray-400">/ 100</span>
        </div>
        <div>
          <p class="font-semibold">Performance score</p>
          <p class="text-sm text-gray-400 mt-0.5">Mobile · Powered by PageSpeed Insights</p>
        </div>
      </div>

      <UAlert
        v-else
        icon="i-heroicons-information-circle"
        color="info"
        variant="subtle"
        title="PageSpeed Insights unavailable — showing resource data only."
        :description="data.pagespeed_error ?? 'Set PAGESPEED_API_KEY env var for full Core Web Vitals.'"
      />

      <!-- Core Web Vitals -->
      <div v-if="data.pagespeed_available" class="flex flex-col gap-3">
        <p class="text-sm font-semibold text-gray-700">Core Web Vitals</p>
        <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
          <div
            v-for="row in vitals"
            :key="row.key"
            class="rounded-lg p-3 border-l-4 flex flex-col gap-0.5"
            :class="vitalBorderClass(vitalStatus(row.vital.score))"
          >
            <span class="text-xl font-bold">{{ row.vital.display ?? '—' }}</span>
            <span class="text-xs font-semibold text-gray-700">{{ row.label }}</span>
            <span class="text-xs text-gray-400">{{ row.hint }}</span>
          </div>
        </div>
      </div>

      <!-- Resource summary -->
      <div class="flex flex-col gap-3">
        <p class="text-sm font-semibold text-gray-700">Page resources</p>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div class="bg-gray-50 rounded-lg p-3 flex flex-col gap-0.5">
            <span class="text-2xl font-bold text-primary-600">{{ data.resources.scripts }}</span>
            <span class="text-xs text-gray-500">Scripts</span>
          </div>
          <div class="bg-gray-50 rounded-lg p-3 flex flex-col gap-0.5">
            <span class="text-2xl font-bold text-primary-600">{{ data.resources.stylesheets }}</span>
            <span class="text-xs text-gray-500">Stylesheets</span>
          </div>
          <div class="bg-gray-50 rounded-lg p-3 flex flex-col gap-0.5">
            <span class="text-2xl font-bold text-primary-600">{{ data.resources.images }}</span>
            <span class="text-xs text-gray-500">Images</span>
          </div>
          <div class="bg-gray-50 rounded-lg p-3 flex flex-col gap-0.5">
            <span class="text-2xl font-bold text-primary-600">{{ data.resources.html_size_kb }} KB</span>
            <span class="text-xs text-gray-500">HTML size</span>
          </div>
        </div>
      </div>
    </div>
  </UCard>
</template>
