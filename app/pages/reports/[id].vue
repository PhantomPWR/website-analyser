<script setup lang="ts">
import SeoSection from '~/components/sections/SeoSection.vue'
import PerformanceSection from '~/components/sections/PerformanceSection.vue'
import SecuritySection from '~/components/sections/SecuritySection.vue'
import TechSection from '~/components/sections/TechSection.vue'
import AccessibilitySection from '~/components/sections/AccessibilitySection.vue'
import ContentSection from '~/components/sections/ContentSection.vue'
import type {
  SeoResult,
  PerformanceResult,
  SecurityResult,
  TechResult,
  AccessibilityResult,
  ContentResult,
} from '~/composables/useAnalyser'

const route = useRoute()
const config = useRuntimeConfig()
const apiBase = config.public.apiBase

interface ReportFull {
  id: string
  url: string
  created_at: string
  data: {
    seo: SeoResult | null
    performance: PerformanceResult | null
    security: SecurityResult | null
    tech: TechResult | null
    accessibility: AccessibilityResult | null
    content: ContentResult | null
  }
}

const { data: report, error } = await useAsyncData<ReportFull>(
  `report-${route.params.id}`,
  () => $fetch(`${apiBase}/reports/${route.params.id}`),
  { server: false },
)

const activeTab = ref('seo')

const tabs = [
  { key: 'seo', label: 'SEO', icon: 'i-heroicons-document-text' },
  { key: 'performance', label: 'Performance', icon: 'i-heroicons-bolt' },
  { key: 'security', label: 'Security', icon: 'i-heroicons-lock-closed' },
  { key: 'technology', label: 'Technology', icon: 'i-heroicons-wrench-screwdriver' },
  { key: 'accessibility', label: 'Accessibility', icon: 'i-heroicons-eye' },
  { key: 'content', label: 'Content', icon: 'i-heroicons-pencil-square' },
]

function formatDate(iso: string) {
  return new Date(iso).toLocaleString()
}

function downloadPdf() {
  window.open(`${apiBase}/reports/${route.params.id}/pdf`, '_blank')
}
</script>

<template>
  <div class="flex flex-col gap-6">
    <UAlert
      v-if="error"
      icon="i-heroicons-exclamation-triangle"
      color="error"
      variant="subtle"
      title="Failed to load report."
    />

    <template v-else-if="report">
      <div class="flex items-start justify-between gap-4">
        <div class="flex flex-col gap-1">
          <UButton
            to="/reports"
            label="All reports"
            icon="i-heroicons-arrow-left"
            variant="ghost"
            color="neutral"
            size="xs"
            class="self-start -ml-2"
          />
          <h1 class="text-xl font-bold text-gray-900 break-all">{{ report.url }}</h1>
          <p class="text-xs text-gray-400">Saved {{ formatDate(report.created_at) }}</p>
        </div>
        <UButton
          label="Download PDF"
          icon="i-heroicons-arrow-down-tray"
          size="sm"
          class="flex-shrink-0"
          @click="downloadPdf"
        />
      </div>

      <div>
        <div class="flex border-b border-gray-200 overflow-x-auto">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            class="flex items-center gap-1.5 px-4 py-2.5 text-sm font-medium whitespace-nowrap transition-colors border-b-2 -mb-px cursor-pointer"
            :class="activeTab === tab.key
              ? 'text-primary-600 border-primary-600'
              : 'text-gray-500 border-transparent hover:text-gray-700'"
            @click="activeTab = tab.key"
          >
            <UIcon :name="tab.icon" class="w-4 h-4" />
            {{ tab.label }}
          </button>
        </div>

        <div class="pt-6">
          <SeoSection v-if="activeTab === 'seo' && report.data.seo" :data="report.data.seo" />
          <PerformanceSection v-else-if="activeTab === 'performance' && report.data.performance" :data="report.data.performance" />
          <SecuritySection v-else-if="activeTab === 'security' && report.data.security" :data="report.data.security" />
          <TechSection v-else-if="activeTab === 'technology' && report.data.tech" :data="report.data.tech" />
          <AccessibilitySection v-else-if="activeTab === 'accessibility' && report.data.accessibility" :data="report.data.accessibility" />
          <ContentSection v-else-if="activeTab === 'content' && report.data.content" :data="report.data.content" />
          <div v-else class="bg-white rounded-xl p-12 text-center text-gray-400 text-sm shadow-sm">
            No data available for this section.
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
