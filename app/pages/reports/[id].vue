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
  { key: 'seo', label: 'SEO', icon: '📄' },
  { key: 'performance', label: 'Performance', icon: '⚡' },
  { key: 'security', label: 'Security', icon: '🔒' },
  { key: 'technology', label: 'Technology', icon: '🛠️' },
  { key: 'accessibility', label: 'Accessibility', icon: '♿' },
  { key: 'content', label: 'Content', icon: '📝' },
]

function formatDate(iso: string) {
  return new Date(iso).toLocaleString()
}

function downloadPdf() {
  window.open(`${apiBase}/reports/${route.params.id}/pdf`, '_blank')
}
</script>

<template>
  <div class="page">
    <div v-if="error" class="error-banner">
      ⚠️ Failed to load report.
    </div>

    <template v-else-if="report">
      <div class="report-header">
        <div class="report-meta">
          <NuxtLink to="/reports" class="back-link">← All reports</NuxtLink>
          <h1 class="report-url">{{ report.url }}</h1>
          <p class="report-date">Saved {{ formatDate(report.created_at) }}</p>
        </div>
        <button class="pdf-btn" @click="downloadPdf">Download PDF</button>
      </div>

      <div class="tabs">
        <nav class="tab-nav">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            class="tab-btn"
            :class="{ 'tab-btn--active': activeTab === tab.key }"
            @click="activeTab = tab.key"
          >
            <span class="tab-icon">{{ tab.icon }}</span>
            {{ tab.label }}
          </button>
        </nav>

        <div class="tab-panel">
          <SeoSection v-if="activeTab === 'seo' && report.data.seo" :data="report.data.seo" />
          <PerformanceSection v-else-if="activeTab === 'performance' && report.data.performance" :data="report.data.performance" />
          <SecuritySection v-else-if="activeTab === 'security' && report.data.security" :data="report.data.security" />
          <TechSection v-else-if="activeTab === 'technology' && report.data.tech" :data="report.data.tech" />
          <AccessibilitySection v-else-if="activeTab === 'accessibility' && report.data.accessibility" :data="report.data.accessibility" />
          <ContentSection v-else-if="activeTab === 'content' && report.data.content" :data="report.data.content" />
          <div v-else class="no-data">No data available for this section.</div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.error-banner {
  background: #fff0f0;
  border: 1px solid #fca5a5;
  color: #b91c1c;
  padding: 1rem 1.25rem;
  border-radius: 8px;
}

.report-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.report-meta {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.back-link {
  font-size: 0.85rem;
  color: #4f46e5;
  text-decoration: none;
  font-weight: 500;
}

.back-link:hover { text-decoration: underline; }

.report-url {
  font-size: 1.3rem;
  font-weight: 700;
  word-break: break-all;
}

.report-date {
  font-size: 0.8rem;
  color: #999;
}

.tabs {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.tab-nav {
  display: flex;
  gap: 0;
  border-bottom: 2px solid #e5e7eb;
  overflow-x: auto;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.7rem 1.1rem;
  font-size: 0.9rem;
  font-weight: 500;
  color: #666;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  cursor: pointer;
  white-space: nowrap;
  transition: color 0.15s, border-color 0.15s;
}

.tab-btn:hover { color: #4f46e5; }

.tab-btn--active {
  color: #4f46e5;
  border-bottom-color: #4f46e5;
  font-weight: 600;
}

.tab-icon { font-size: 1rem; }

.tab-panel { padding-top: 1.5rem; }

.no-data {
  background: #fff;
  border-radius: 12px;
  padding: 3rem;
  text-align: center;
  color: #aaa;
  font-size: 0.95rem;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.pdf-btn {
  align-self: flex-start;
  padding: 0.55rem 1.1rem;
  font-size: 0.88rem;
  font-weight: 600;
  color: #fff;
  background: #4f46e5;
  border: none;
  border-radius: 7px;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.15s;
}

.pdf-btn:hover { background: #4338ca; }
</style>
