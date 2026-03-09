<script setup lang="ts">
import type { AccessibilityResult } from '~/composables/useAnalyser'

const props = defineProps<{ data: AccessibilityResult }>()

type Status = 'pass' | 'warn' | 'fail'

function scoreStatus(s: number): Status {
  if (s >= 80) return 'pass'
  if (s >= 50) return 'warn'
  return 'fail'
}

interface Check {
  label: string
  status: Status
  detail: string
}

const checks = computed<Check[]>(() => {
  const d = props.data
  return [
    {
      label: 'Language attribute',
      status: d.lang_present ? 'pass' : 'fail',
      detail: d.lang_present ? `lang="${d.lang_attribute}"` : 'Missing lang attribute on <html>',
    },
    {
      label: 'Image alt text',
      status: d.images_missing_alt === 0 && d.images_empty_alt === 0
        ? 'pass'
        : d.images_missing_alt > 3 || d.images_empty_alt > 3 ? 'fail' : 'warn',
      detail: d.total_images === 0
        ? 'No images found'
        : `${d.total_images} images — ${d.images_missing_alt} missing alt, ${d.images_empty_alt} empty alt`,
    },
    {
      label: 'Form labels',
      status: d.inputs_missing_label === 0 ? 'pass' : d.inputs_missing_label > 3 ? 'fail' : 'warn',
      detail: d.total_inputs === 0
        ? 'No form inputs found'
        : `${d.total_inputs} inputs — ${d.inputs_missing_label} missing label`,
    },
    {
      label: 'Heading order',
      status: d.heading_order_valid ? 'pass' : 'warn',
      detail: d.heading_order_valid ? 'Heading hierarchy is valid' : `${d.heading_issues.length} issue(s) found`,
    },
    {
      label: 'Skip navigation link',
      status: d.skip_link_present ? 'pass' : 'warn',
      detail: d.skip_link_present ? 'Skip link detected' : 'No skip link found (recommended for keyboard users)',
    },
    {
      label: 'ARIA landmarks',
      status: d.aria_landmarks.length >= 3 ? 'pass' : d.aria_landmarks.length > 0 ? 'warn' : 'fail',
      detail: d.aria_landmarks.length > 0
        ? d.aria_landmarks.join(', ')
        : 'No ARIA landmarks or semantic HTML5 elements detected',
    },
    {
      label: 'Positive tabindex',
      status: d.positive_tabindex_count === 0 ? 'pass' : 'warn',
      detail: d.positive_tabindex_count === 0
        ? 'No positive tabindex values found'
        : `${d.positive_tabindex_count} element(s) with positive tabindex (disrupts tab order)`,
    },
  ]
})
</script>

<template>
  <section class="section-card">
    <h2 class="section-title">
      <span class="section-icon">♿</span> Accessibility
    </h2>

    <!-- Score -->
    <div class="score-row">
      <div class="score-ring" :class="`ring--${scoreStatus(data.score)}`">
        <span class="score-value">{{ data.score }}</span>
        <span class="score-label">/ 100</span>
      </div>
      <div class="score-meta">
        <p class="score-heading">Accessibility score</p>
        <p class="score-sub">{{ data.issues_total }} issue{{ data.issues_total !== 1 ? 's' : '' }} found</p>
      </div>
    </div>

    <!-- Checks -->
    <div class="checks">
      <h3 class="block-title">Checks</h3>
      <div
        v-for="check in checks"
        :key="check.label"
        class="check-row"
      >
        <span class="check-badge" :class="`badge--${check.status}`">
          {{ check.status === 'pass' ? '✓' : check.status === 'warn' ? '!' : '✗' }}
        </span>
        <div class="check-body">
          <span class="check-label">{{ check.label }}</span>
          <span class="check-detail">{{ check.detail }}</span>
        </div>
      </div>
    </div>

    <!-- Image issues -->
    <div v-if="data.image_issues.length" class="issue-block">
      <h3 class="block-title">Image alt issues ({{ data.image_issues.length }})</h3>
      <div class="issue-list">
        <div v-for="(issue, i) in data.image_issues" :key="i" class="issue-row">
          <span class="issue-badge" :class="issue.issue === 'missing_alt' ? 'badge--fail' : 'badge--warn'">
            {{ issue.issue === 'missing_alt' ? '✗' : '!' }}
          </span>
          <div class="issue-body">
            <span class="issue-tag">{{ issue.issue === 'missing_alt' ? 'Missing alt' : 'Empty alt' }}</span>
            <span class="issue-src">{{ issue.src || '(no src)' }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Heading issues -->
    <div v-if="data.heading_issues.length" class="issue-block">
      <h3 class="block-title">Heading issues</h3>
      <div class="issue-list">
        <div v-for="(issue, i) in data.heading_issues" :key="i" class="issue-row">
          <span class="issue-badge badge--warn">!</span>
          <div class="issue-body">
            <span class="issue-tag">{{ issue.tag.toUpperCase() }}: {{ issue.issue }}</span>
            <span v-if="issue.text" class="issue-src">"{{ issue.text }}"</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Form issues -->
    <div v-if="data.form_issues.length" class="issue-block">
      <h3 class="block-title">Form label issues ({{ data.form_issues.length }})</h3>
      <div class="issue-list">
        <div v-for="(issue, i) in data.form_issues" :key="i" class="issue-row">
          <span class="issue-badge badge--fail">✗</span>
          <div class="issue-body">
            <span class="issue-tag">
              {{ issue.element }}<span v-if="issue.input_type"> [type="{{ issue.input_type }}"]</span>
            </span>
            <span class="issue-src">{{ issue.issue }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ARIA summary -->
    <div class="aria-block">
      <h3 class="block-title">ARIA usage</h3>
      <div class="aria-grid">
        <div class="aria-stat">
          <span class="aria-count">{{ data.aria_roles_count }}</span>
          <span class="aria-label">ARIA roles</span>
        </div>
        <div class="aria-stat">
          <span class="aria-count">{{ data.aria_labels_count }}</span>
          <span class="aria-label">aria-label attrs</span>
        </div>
        <div class="aria-stat">
          <span class="aria-count">{{ data.aria_landmarks.length }}</span>
          <span class="aria-label">Landmarks</span>
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

.score-value { font-size: 1.4rem; font-weight: 700; line-height: 1; }
.score-label { font-size: 0.7rem; color: #888; }
.score-heading { font-weight: 600; font-size: 1rem; }
.score-sub { font-size: 0.8rem; color: #888; margin-top: 0.2rem; }

.block-title {
  font-size: 0.95rem;
  font-weight: 600;
  margin-bottom: 0.6rem;
}

.checks {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.check-row {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.6rem 0.75rem;
  background: #f9fafb;
  border-radius: 6px;
}

.check-badge, .issue-badge {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 700;
  flex-shrink: 0;
  margin-top: 1px;
}

.badge--pass { background: #d1fae5; color: #065f46; }
.badge--warn { background: #fef3c7; color: #92400e; }
.badge--fail { background: #fee2e2; color: #991b1b; }

.check-body, .issue-body {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  min-width: 0;
}

.check-label, .issue-tag { font-weight: 500; font-size: 0.9rem; }
.check-detail, .issue-src { font-size: 0.78rem; color: #666; word-break: break-all; }

.issue-block { display: flex; flex-direction: column; }

.issue-list {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.issue-row {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  padding: 0.4rem 0.5rem;
  border-radius: 6px;
  background: #fafafa;
}

.aria-block { display: flex; flex-direction: column; }

.aria-grid {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.aria-stat {
  background: #f5f3ff;
  border: 1px solid #ede9fe;
  border-radius: 8px;
  padding: 0.75rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  min-width: 100px;
  text-align: center;
}

.aria-count {
  font-size: 1.4rem;
  font-weight: 700;
  color: #4f46e5;
}

.aria-label {
  font-size: 0.75rem;
  color: #666;
}
</style>
