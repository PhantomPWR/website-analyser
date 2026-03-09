<script setup lang="ts">
import type { PerformanceResult, WebVital } from '~/composables/useAnalyser'

const props = defineProps<{ data: PerformanceResult }>()

function scoreColor(score: number | null): 'pass' | 'warn' | 'fail' {
  if (score === null) return 'warn'
  if (score >= 0.9) return 'pass'
  if (score >= 0.5) return 'warn'
  return 'fail'
}

function perfScoreColor(score: number | null): 'pass' | 'warn' | 'fail' {
  if (score === null) return 'warn'
  if (score >= 90) return 'pass'
  if (score >= 50) return 'warn'
  return 'fail'
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
</script>

<template>
  <section class="section-card">
    <h2 class="section-title">
      <span class="section-icon">⚡</span> Performance
    </h2>

    <!-- Overall score -->
    <div v-if="data.pagespeed_available" class="score-row">
      <div class="score-ring" :class="`ring--${perfScoreColor(data.performance_score)}`">
        <span class="score-value">{{ data.performance_score ?? '—' }}</span>
        <span class="score-label">/ 100</span>
      </div>
      <div class="score-meta">
        <p class="score-heading">Performance score</p>
        <p class="score-sub">Mobile · Powered by PageSpeed Insights</p>
      </div>
    </div>
    <div v-else class="info-banner">
      ℹ️ PageSpeed Insights unavailable — showing resource data only.<br />
      <span v-if="data.pagespeed_error" class="error-detail">{{ data.pagespeed_error }}</span>
      <span v-else>Set <code>PAGESPEED_API_KEY</code> env var for full Core Web Vitals.</span>
    </div>

    <!-- Core Web Vitals -->
    <div v-if="data.pagespeed_available" class="vitals">
      <h3 class="block-title">Core Web Vitals</h3>
      <div class="vitals-grid">
        <div
          v-for="row in vitals"
          :key="row.key"
          class="vital-card"
          :class="`vital-card--${scoreColor(row.vital.score)}`"
        >
          <span class="vital-display">{{ row.vital.display ?? '—' }}</span>
          <span class="vital-name">{{ row.label }}</span>
          <span class="vital-hint">{{ row.hint }}</span>
        </div>
      </div>
    </div>

    <!-- Resource summary -->
    <div class="resources">
      <h3 class="block-title">Page resources</h3>
      <div class="resource-grid">
        <div class="resource-item">
          <span class="resource-count">{{ data.resources.scripts }}</span>
          <span class="resource-label">Scripts</span>
        </div>
        <div class="resource-item">
          <span class="resource-count">{{ data.resources.stylesheets }}</span>
          <span class="resource-label">Stylesheets</span>
        </div>
        <div class="resource-item">
          <span class="resource-count">{{ data.resources.images }}</span>
          <span class="resource-label">Images</span>
        </div>
        <div class="resource-item">
          <span class="resource-count">{{ data.resources.html_size_kb }} KB</span>
          <span class="resource-label">HTML size</span>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.section-card {
  background: #fff;
  border-radius: 12px;
  padding: 1.75rem;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.section-title {
  font-size: 1.2rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.section-icon { font-size: 1.3rem; }

/* Score ring */
.score-row {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.score-ring {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  border: 5px solid;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.ring--pass { border-color: #10b981; }
.ring--warn { border-color: #f59e0b; }
.ring--fail { border-color: #ef4444; }

.score-value {
  font-size: 1.4rem;
  font-weight: 700;
  line-height: 1;
}

.score-label {
  font-size: 0.7rem;
  color: #888;
}

.score-heading {
  font-weight: 600;
  font-size: 1rem;
}

.score-sub {
  font-size: 0.8rem;
  color: #888;
  margin-top: 0.2rem;
}

/* Vitals grid */
.block-title {
  font-size: 0.95rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.vitals-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 0.75rem;
}

.vital-card {
  border-radius: 8px;
  padding: 0.9rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  border-left: 4px solid;
}

.vital-card--pass { background: #f0fdf4; border-color: #10b981; }
.vital-card--warn { background: #fffbeb; border-color: #f59e0b; }
.vital-card--fail { background: #fff1f2; border-color: #ef4444; }

.vital-display {
  font-size: 1.2rem;
  font-weight: 700;
}

.vital-name {
  font-size: 0.78rem;
  font-weight: 600;
  color: #333;
}

.vital-hint {
  font-size: 0.72rem;
  color: #888;
}

/* Resources */
.resource-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 0.75rem;
}

.resource-item {
  background: #f9fafb;
  border-radius: 8px;
  padding: 0.9rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.resource-count {
  font-size: 1.4rem;
  font-weight: 700;
  color: #4f46e5;
}

.resource-label {
  font-size: 0.78rem;
  color: #666;
}

.info-banner {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  color: #1d4ed8;
  padding: 0.85rem 1rem;
  border-radius: 8px;
  font-size: 0.88rem;
}

.info-banner code {
  background: #dbeafe;
  padding: 0.1rem 0.3rem;
  border-radius: 4px;
  font-size: 0.85em;
}

.error-detail {
  font-family: monospace;
  font-size: 0.8em;
  word-break: break-all;
}
</style>
