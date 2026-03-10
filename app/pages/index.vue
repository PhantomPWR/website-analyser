<script setup lang="ts">
import SeoSection from '~/components/sections/SeoSection.vue'
import PerformanceSection from '~/components/sections/PerformanceSection.vue'
import SecuritySection from '~/components/sections/SecuritySection.vue'
import TechSection from '~/components/sections/TechSection.vue'
import AccessibilitySection from '~/components/sections/AccessibilitySection.vue'
import ContentSection from '~/components/sections/ContentSection.vue'

const { loading, error, saving, savedReportId, results, analysedUrl, analyseUrl, saveReport } = useAnalyser()

const inputUrl = ref('')
const activeTab = ref('seo')

const tabs = [
  { key: 'seo', label: 'SEO', icon: 'i-heroicons-document-text' },
  { key: 'performance', label: 'Performance', icon: 'i-heroicons-bolt' },
  { key: 'security', label: 'Security', icon: 'i-heroicons-lock-closed' },
  { key: 'technology', label: 'Technology', icon: 'i-heroicons-wrench-screwdriver' },
  { key: 'accessibility', label: 'Accessibility', icon: 'i-heroicons-eye' },
  { key: 'content', label: 'Content', icon: 'i-heroicons-pencil-square' },
]

function normaliseUrl(raw: string): string {
  const trimmed = raw.trim()
  if (!trimmed.startsWith('http://') && !trimmed.startsWith('https://')) {
    return `https://${trimmed}`
  }
  return trimmed
}

async function handleSubmit() {
  if (!inputUrl.value.trim()) return
  activeTab.value = 'seo'
  await analyseUrl(normaliseUrl(inputUrl.value))
}
</script>

<template>
  <div class="flex flex-col gap-8">
    <!-- Hero -->
    <section class="text-center pt-10 pb-4">
      <h1 class="text-4xl font-bold text-gray-900 mb-2">Analyse any website</h1>
      <p class="text-gray-500 mb-8">SEO, Performance, Security, Accessibility &amp; more</p>

      <form class="flex gap-3 max-w-2xl mx-auto" @submit.prevent="handleSubmit">
        <UInput
          v-model="inputUrl"
          placeholder="https://example.com"
          :disabled="loading"
          autocomplete="off"
          size="xl"
          icon="i-heroicons-globe-alt"
          class="flex-1"
        />
        <UButton
          type="submit"
          size="xl"
          :loading="loading"
          :disabled="!inputUrl.trim()"
          label="Analyse"
        />
      </form>
    </section>

    <!-- Error -->
    <UAlert
      v-if="error"
      icon="i-heroicons-exclamation-triangle"
      color="error"
      variant="subtle"
      :title="error"
    />

    <!-- Results -->
    <div v-if="analysedUrl && !loading && !error" class="flex flex-col gap-4">
      <!-- Results header -->
      <div class="flex items-center justify-between gap-4 flex-wrap">
        <p class="text-sm text-gray-500">
          Results for <strong class="text-gray-800">{{ analysedUrl }}</strong>
        </p>
        <div class="flex items-center gap-3">
          <UButton
            v-if="savedReportId"
            :to="`/reports/${savedReportId}`"
            label="View saved report"
            icon="i-heroicons-arrow-right"
            trailing
            color="success"
            variant="subtle"
            size="sm"
          />
          <UButton
            v-else
            icon="i-heroicons-bookmark"
            label="Save report"
            variant="outline"
            size="sm"
            :loading="saving"
            @click="saveReport"
          />
        </div>
      </div>

      <!-- Tabs -->
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
          <SeoSection v-if="activeTab === 'seo' && results.seo" :data="results.seo" />
          <PerformanceSection v-else-if="activeTab === 'performance' && results.performance" :data="results.performance" />
          <SecuritySection v-else-if="activeTab === 'security' && results.security" :data="results.security" />
          <TechSection v-else-if="activeTab === 'technology' && results.tech" :data="results.tech" />
          <AccessibilitySection v-else-if="activeTab === 'accessibility' && results.accessibility" :data="results.accessibility" />
          <ContentSection v-else-if="activeTab === 'content' && results.content" :data="results.content" />
          <div v-else class="bg-white rounded-xl p-12 text-center text-gray-400 shadow-sm text-sm">
            No data for this section.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
