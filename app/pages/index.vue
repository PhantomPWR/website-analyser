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
  { key: 'seo', label: 'SEO', icon: '📄' },
  { key: 'performance', label: 'Performance', icon: '⚡' },
  { key: 'security', label: 'Security', icon: '🔒' },
  { key: 'technology', label: 'Technology', icon: '🛠️' },
  { key: 'accessibility', label: 'Accessibility', icon: '♿' },
  { key: 'content', label: 'Content', icon: '📝' },
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
  <div class="page">
    <section class="hero">
      <h1 class="hero-title">Analyse any website</h1>
      <p class="hero-subtitle">SEO, Performance, Security, Accessibility &amp; more</p>

      <form class="search-form" @submit.prevent="handleSubmit">
        <input
          v-model="inputUrl"
          type="text"
          class="url-input"
          placeholder="https://example.com"
          :disabled="loading"
          autocomplete="off"
          spellcheck="false"
        />
        <button type="submit" class="analyse-btn" :disabled="loading || !inputUrl.trim()">
          <span v-if="loading" class="spinner" />
          <span v-else>Analyse</span>
        </button>
      </form>
    </section>

    <div v-if="error" class="error-banner">
      ⚠️ {{ error }}
    </div>

    <div v-if="analysedUrl && !loading && !error" class="results">
      <div class="results-header">
        <p class="results-url">Results for <strong>{{ analysedUrl }}</strong></p>
        <div class="results-actions">
          <NuxtLink v-if="savedReportId" :to="`/reports/${savedReportId}`" class="view-btn">
            View saved report →
          </NuxtLink>
          <button v-else class="save-btn" :disabled="saving" @click="saveReport">
            <span v-if="saving" class="spinner-sm" />
            <span v-else>💾 Save report</span>
          </button>
        </div>
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
          <SeoSection v-if="activeTab === 'seo' && results.seo" :data="results.seo" />
          <PerformanceSection v-else-if="activeTab === 'performance' && results.performance" :data="results.performance" />
          <SecuritySection v-else-if="activeTab === 'security' && results.security" :data="results.security" />
          <TechSection v-else-if="activeTab === 'technology' && results.tech" :data="results.tech" />
          <AccessibilitySection v-else-if="activeTab === 'accessibility' && results.accessibility" :data="results.accessibility" />
          <ContentSection v-else-if="activeTab === 'content' && results.content" :data="results.content" />
          <div v-else class="coming-soon">
            Coming soon
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.hero {
  text-align: center;
  padding: 3rem 1rem 2rem;
}

.hero-title {
  font-size: 2.2rem;
  font-weight: 700;
  color: #1a1a2e;
  margin-bottom: 0.5rem;
}

.hero-subtitle {
  font-size: 1rem;
  color: #666;
  margin-bottom: 2rem;
}

.search-form {
  display: flex;
  gap: 0.75rem;
  max-width: 680px;
  margin: 0 auto;
}

.url-input {
  flex: 1;
  padding: 0.75rem 1rem;
  font-size: 1rem;
  border: 2px solid #dde3ee;
  border-radius: 8px;
  outline: none;
  transition: border-color 0.2s;
  background: #fff;
}

.url-input:focus {
  border-color: #4f46e5;
}

.url-input:disabled {
  background: #f0f0f0;
}

.analyse-btn {
  padding: 0.75rem 1.5rem;
  background: #4f46e5;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  min-width: 110px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.analyse-btn:hover:not(:disabled) {
  background: #4338ca;
}

.analyse-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-banner {
  background: #fff0f0;
  border: 1px solid #fca5a5;
  color: #b91c1c;
  padding: 1rem 1.25rem;
  border-radius: 8px;
}

.results {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.results-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.results-url {
  font-size: 0.9rem;
  color: #555;
}

.results-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.save-btn {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.45rem 1rem;
  background: #fff;
  color: #4f46e5;
  border: 1.5px solid #4f46e5;
  border-radius: 7px;
  font-size: 0.88rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}

.save-btn:hover:not(:disabled) {
  background: #4f46e5;
  color: #fff;
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.view-btn {
  padding: 0.45rem 1rem;
  background: #d1fae5;
  color: #065f46;
  border-radius: 7px;
  font-size: 0.88rem;
  font-weight: 600;
  text-decoration: none;
  transition: background 0.15s;
}

.view-btn:hover {
  background: #a7f3d0;
}

.spinner-sm {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(79, 70, 229, 0.3);
  border-top-color: #4f46e5;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
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

.tab-btn:hover {
  color: #4f46e5;
}

.tab-btn--active {
  color: #4f46e5;
  border-bottom-color: #4f46e5;
  font-weight: 600;
}

.tab-icon {
  font-size: 1rem;
}

.tab-panel {
  padding-top: 1.5rem;
}

.coming-soon {
  background: #fff;
  border-radius: 12px;
  padding: 3rem;
  text-align: center;
  color: #aaa;
  font-size: 0.95rem;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}
</style>
