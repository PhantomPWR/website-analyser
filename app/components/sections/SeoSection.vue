<script setup lang="ts">
import type { SeoResult } from '~/composables/useAnalyser'

const props = defineProps<{ data: SeoResult }>()

interface Check {
  label: string
  value: string | null
  status: 'pass' | 'warn' | 'fail'
  detail?: string
}

const checks = computed<Check[]>(() => {
  const d = props.data
  return [
    {
      label: 'Title tag',
      value: d.title,
      status: !d.title ? 'fail' : d.title.length < 10 || d.title.length > 70 ? 'warn' : 'pass',
      detail: d.title ? `${d.title.length} characters` : 'Missing',
    },
    {
      label: 'Meta description',
      value: d.description,
      status: !d.description ? 'fail' : d.description.length < 50 || d.description.length > 160 ? 'warn' : 'pass',
      detail: d.description ? `${d.description.length} characters` : 'Missing',
    },
    {
      label: 'Canonical URL',
      value: d.canonical,
      status: d.canonical ? 'pass' : 'warn',
      detail: d.canonical ?? 'Not set',
    },
    {
      label: 'Robots meta',
      value: d.robots_meta,
      status: d.robots_meta ? 'pass' : 'warn',
      detail: d.robots_meta ?? 'Not set (defaults to index, follow)',
    },
    {
      label: 'robots.txt',
      value: String(d.robots_txt_found),
      status: d.robots_txt_found ? 'pass' : 'warn',
      detail: d.robots_txt_found ? 'Found' : 'Not found',
    },
    {
      label: 'Sitemap',
      value: String(d.sitemap_found),
      status: d.sitemap_found ? 'pass' : 'warn',
      detail: d.sitemap_found ? 'Found at /sitemap.xml' : 'Not found at /sitemap.xml',
    },
    {
      label: 'Open Graph tags',
      value: Object.keys(d.og_tags).length > 0 ? 'present' : null,
      status: Object.keys(d.og_tags).length >= 3 ? 'pass' : Object.keys(d.og_tags).length > 0 ? 'warn' : 'fail',
      detail: Object.keys(d.og_tags).length > 0 ? Object.keys(d.og_tags).join(', ') : 'None found',
    },
    {
      label: 'Structured data',
      value: d.structured_data.length > 0 ? 'present' : null,
      status: d.structured_data.length > 0 ? 'pass' : 'warn',
      detail: d.structured_data.length > 0 ? `${d.structured_data.length} JSON-LD block(s)` : 'None found',
    },
  ]
})

const h1Count = computed(() => props.data.headings.h1?.length ?? 0)
const h1Status = computed(() => {
  if (h1Count.value === 0) return 'fail'
  if (h1Count.value > 1) return 'warn'
  return 'pass'
})
</script>

<template>
  <section class="section-card">
    <h2 class="section-title">
      <span class="section-icon">📄</span> SEO
    </h2>

    <div class="checks">
      <div
        v-for="check in checks"
        :key="check.label"
        class="check-row"
        :class="`check-row--${check.status}`"
      >
        <span class="check-badge" :class="`badge--${check.status}`">
          {{ check.status === 'pass' ? '✓' : check.status === 'warn' ? '!' : '✗' }}
        </span>
        <span class="check-label">{{ check.label }}</span>
        <span class="check-detail">{{ check.detail }}</span>
      </div>
    </div>

    <div class="headings-block">
      <h3 class="block-title">
        Heading structure
        <span class="badge" :class="`badge--${h1Status}`">
          H1: {{ h1Count }}
        </span>
      </h3>
      <div v-for="level in ['h1','h2','h3','h4','h5','h6']" :key="level">
        <div v-if="data.headings[level]?.length" class="heading-group">
          <span class="heading-level">{{ level.toUpperCase() }}</span>
          <ul class="heading-list">
            <li v-for="text in data.headings[level]" :key="text" class="heading-item">
              {{ text }}
            </li>
          </ul>
        </div>
      </div>
      <p v-if="Object.keys(data.headings).length === 0" class="no-data">No headings found.</p>
    </div>

    <div v-if="Object.keys(data.og_tags).length" class="og-block">
      <h3 class="block-title">Open Graph tags</h3>
      <table class="tag-table">
        <tbody>
          <tr v-for="(val, key) in data.og_tags" :key="key">
            <td class="tag-key">{{ key }}</td>
            <td class="tag-val">{{ val }}</td>
          </tr>
        </tbody>
      </table>
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

.section-icon {
  font-size: 1.3rem;
}

.checks {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.check-row {
  display: grid;
  grid-template-columns: 28px 200px 1fr;
  align-items: center;
  gap: 0.75rem;
  padding: 0.6rem 0.75rem;
  border-radius: 6px;
  background: #f9fafb;
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
  flex-shrink: 0;
}

.badge--pass { background: #d1fae5; color: #065f46; }
.badge--warn { background: #fef3c7; color: #92400e; }
.badge--fail { background: #fee2e2; color: #991b1b; }

.check-label {
  font-weight: 500;
  font-size: 0.9rem;
}

.check-detail {
  font-size: 0.85rem;
  color: #555;
  word-break: break-all;
}

.headings-block,
.og-block {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.block-title {
  font-size: 0.95rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.badge {
  padding: 0.15rem 0.5rem;
  border-radius: 99px;
  font-size: 0.75rem;
  font-weight: 600;
}

.heading-group {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
}

.heading-level {
  font-size: 0.7rem;
  font-weight: 700;
  color: #888;
  background: #f0f0f0;
  border-radius: 4px;
  padding: 0.1rem 0.4rem;
  margin-top: 0.2rem;
  min-width: 28px;
  text-align: center;
}

.heading-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.heading-item {
  font-size: 0.88rem;
  color: #333;
}

.no-data {
  font-size: 0.88rem;
  color: #999;
}

.tag-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}

.tag-table tr:not(:last-child) td {
  border-bottom: 1px solid #f0f0f0;
}

.tag-key {
  padding: 0.4rem 0.75rem 0.4rem 0;
  font-weight: 500;
  color: #555;
  white-space: nowrap;
  width: 200px;
}

.tag-val {
  padding: 0.4rem 0;
  word-break: break-all;
  color: #333;
}
</style>
