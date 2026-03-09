<script setup lang="ts">
import type { ContentResult } from '~/composables/useAnalyser'

const props = defineProps<{ data: ContentResult }>()

type Status = 'pass' | 'warn' | 'fail'

function readabilityStatus(score: number): Status {
  if (score >= 60) return 'pass'
  if (score >= 30) return 'warn'
  return 'fail'
}

function wordCountStatus(count: number): Status {
  if (count >= 300) return 'pass'
  if (count >= 100) return 'warn'
  return 'fail'
}

function ratioStatus(ratio: number): Status {
  if (ratio >= 20) return 'pass'
  if (ratio >= 10) return 'warn'
  return 'fail'
}

interface StatCard {
  label: string
  value: string
  sub?: string
  status?: Status
}

const stats = computed<StatCard[]>(() => [
  {
    label: 'Word count',
    value: props.data.word_count.toLocaleString(),
    sub: props.data.word_count < 300 ? 'Aim for 300+ for good SEO' : 'Good',
    status: wordCountStatus(props.data.word_count),
  },
  {
    label: 'Sentences',
    value: props.data.sentence_count.toLocaleString(),
    sub: `~${props.data.avg_words_per_sentence} words/sentence`,
  },
  {
    label: 'Paragraphs',
    value: props.data.paragraph_count.toLocaleString(),
  },
  {
    label: 'Content ratio',
    value: `${props.data.content_to_html_ratio}%`,
    sub: 'Text vs total HTML',
    status: ratioStatus(props.data.content_to_html_ratio),
  },
])

const linkStats = computed<StatCard[]>(() => [
  {
    label: 'Internal links',
    value: props.data.internal_links_total.toLocaleString(),
  },
  {
    label: 'External links',
    value: props.data.external_links_total.toLocaleString(),
  },
  {
    label: 'Broken links',
    value: props.data.broken_links.length.toLocaleString(),
    sub: `of ${props.data.internal_links_checked} checked`,
    status: props.data.broken_links.length === 0 ? 'pass' : 'fail',
  },
])
</script>

<template>
  <section class="section-card">
    <h2 class="section-title">
      <span class="section-icon">📝</span> Content
    </h2>

    <!-- Readability -->
    <div class="readability-row">
      <div class="flesch-ring" :class="`ring--${readabilityStatus(data.flesch_reading_ease)}`">
        <span class="flesch-score">{{ data.flesch_reading_ease }}</span>
        <span class="flesch-label">/ 100</span>
      </div>
      <div class="flesch-meta">
        <p class="flesch-heading">Flesch Reading Ease</p>
        <p class="flesch-grade" :class="`grade--${readabilityStatus(data.flesch_reading_ease)}`">
          {{ data.readability_label }}
        </p>
        <p class="flesch-sub">60–70 is considered ideal for general audiences</p>
      </div>
    </div>

    <!-- Content stats -->
    <div class="block">
      <h3 class="block-title">Content stats</h3>
      <div class="stat-grid">
        <div
          v-for="stat in stats"
          :key="stat.label"
          class="stat-card"
          :class="stat.status ? `stat--${stat.status}` : ''"
        >
          <span class="stat-value">{{ stat.value }}</span>
          <span class="stat-label">{{ stat.label }}</span>
          <span v-if="stat.sub" class="stat-sub">{{ stat.sub }}</span>
        </div>
      </div>
    </div>

    <!-- Links -->
    <div class="block">
      <h3 class="block-title">Links</h3>
      <div class="stat-grid">
        <div
          v-for="stat in linkStats"
          :key="stat.label"
          class="stat-card"
          :class="stat.status ? `stat--${stat.status}` : ''"
        >
          <span class="stat-value">{{ stat.value }}</span>
          <span class="stat-label">{{ stat.label }}</span>
          <span v-if="stat.sub" class="stat-sub">{{ stat.sub }}</span>
        </div>
      </div>

      <div v-if="data.broken_links.length" class="broken-links">
        <div v-for="link in data.broken_links" :key="link.url" class="broken-row">
          <span class="broken-badge">
            {{ link.status_code ?? 'ERR' }}
          </span>
          <span class="broken-url">{{ link.url }}</span>
          <span v-if="link.error" class="broken-error">{{ link.error }}</span>
        </div>
      </div>
    </div>

    <!-- Misc checks -->
    <div class="block">
      <h3 class="block-title">Misc checks</h3>
      <div class="checks">
        <div class="check-row">
          <span class="check-badge" :class="data.has_favicon ? 'badge--pass' : 'badge--warn'">
            {{ data.has_favicon ? '✓' : '!' }}
          </span>
          <span class="check-label">Favicon</span>
          <span class="check-detail">{{ data.has_favicon ? 'Found' : 'Not found' }}</span>
        </div>
        <div class="check-row">
          <span class="check-badge" :class="data.has_meta_viewport ? 'badge--pass' : 'badge--fail'">
            {{ data.has_meta_viewport ? '✓' : '✗' }}
          </span>
          <span class="check-label">Meta viewport</span>
          <span class="check-detail">{{ data.has_meta_viewport ? 'Present' : 'Missing — required for mobile' }}</span>
        </div>
      </div>
    </div>

    <!-- Text preview -->
    <div v-if="data.text_preview" class="block">
      <h3 class="block-title">Content preview</h3>
      <p class="text-preview">{{ data.text_preview }}</p>
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

/* Readability ring */
.readability-row {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.flesch-ring {
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

.flesch-score { font-size: 1.4rem; font-weight: 700; line-height: 1; }
.flesch-label { font-size: 0.7rem; color: #888; }
.flesch-heading { font-weight: 600; font-size: 1rem; }
.flesch-grade { font-size: 0.9rem; font-weight: 600; margin-top: 0.15rem; }
.grade--pass { color: #065f46; }
.grade--warn { color: #92400e; }
.grade--fail { color: #991b1b; }
.flesch-sub { font-size: 0.75rem; color: #888; margin-top: 0.2rem; }

/* Stats */
.block { display: flex; flex-direction: column; gap: 0.75rem; }

.block-title {
  font-size: 0.95rem;
  font-weight: 600;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 0.75rem;
}

.stat-card {
  background: #f9fafb;
  border-radius: 8px;
  padding: 0.85rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  border-left: 3px solid #e5e7eb;
}

.stat--pass { border-color: #10b981; }
.stat--warn { border-color: #f59e0b; }
.stat--fail { border-color: #ef4444; }

.stat-value { font-size: 1.4rem; font-weight: 700; color: #1a1a2e; }
.stat-label { font-size: 0.78rem; font-weight: 600; color: #555; }
.stat-sub { font-size: 0.72rem; color: #888; }

/* Broken links */
.broken-links {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  margin-top: 0.25rem;
}

.broken-row {
  display: flex;
  align-items: baseline;
  gap: 0.6rem;
  padding: 0.35rem 0.5rem;
  background: #fff1f2;
  border-radius: 6px;
  font-size: 0.82rem;
}

.broken-badge {
  background: #fee2e2;
  color: #991b1b;
  font-weight: 700;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  font-size: 0.75rem;
  flex-shrink: 0;
}

.broken-url {
  color: #b91c1c;
  word-break: break-all;
  flex: 1;
}

.broken-error {
  color: #888;
  font-size: 0.75rem;
  white-space: nowrap;
}

/* Misc checks */
.checks { display: flex; flex-direction: column; gap: 0.4rem; }

.check-row {
  display: grid;
  grid-template-columns: 28px 160px 1fr;
  align-items: center;
  gap: 0.6rem;
  padding: 0.5rem 0.75rem;
  background: #f9fafb;
  border-radius: 6px;
}

.check-badge {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 700;
}

.badge--pass { background: #d1fae5; color: #065f46; }
.badge--warn { background: #fef3c7; color: #92400e; }
.badge--fail { background: #fee2e2; color: #991b1b; }

.check-label { font-weight: 500; font-size: 0.9rem; }
.check-detail { font-size: 0.82rem; color: #666; }

/* Preview */
.text-preview {
  font-size: 0.88rem;
  color: #555;
  line-height: 1.6;
  background: #f9fafb;
  padding: 0.85rem 1rem;
  border-radius: 8px;
  border-left: 3px solid #e5e7eb;
}
</style>
