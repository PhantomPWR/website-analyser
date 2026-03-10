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

function ringClass(s: Status) {
  return s === 'pass' ? 'border-green-500' : s === 'warn' ? 'border-amber-500' : 'border-red-500'
}

function statusColor(s: Status) {
  return s === 'pass' ? 'success' : s === 'warn' ? 'warning' : 'error'
}

function statusIcon(s: Status) {
  return s === 'pass' ? '✓' : s === 'warn' ? '!' : '✗'
}

const overallStatus = computed(() => scoreStatus(props.data.score))
</script>

<template>
  <UCard>
    <template #header>
      <div class="flex items-center gap-2">
        <UIcon name="i-heroicons-eye" class="w-5 h-5 text-primary-500" />
        <h2 class="text-lg font-bold">Accessibility</h2>
      </div>
    </template>

    <div class="flex flex-col gap-6">
      <!-- Score ring -->
      <div class="flex items-center gap-5">
        <div
          class="w-20 h-20 rounded-full border-[5px] flex flex-col items-center justify-center flex-shrink-0"
          :class="ringClass(overallStatus)"
        >
          <span class="text-xl font-bold leading-none">{{ data.score }}</span>
          <span class="text-xs text-gray-400">/ 100</span>
        </div>
        <div>
          <p class="font-semibold">Accessibility score</p>
          <p class="text-sm text-gray-400 mt-0.5">
            {{ data.issues_total }} issue{{ data.issues_total !== 1 ? 's' : '' }} found
          </p>
        </div>
      </div>

      <!-- Checks -->
      <div class="flex flex-col gap-2">
        <p class="text-sm font-semibold text-gray-700">Checks</p>
        <div
          v-for="check in checks"
          :key="check.label"
          class="flex items-start gap-3 bg-gray-50 rounded-lg px-3 py-2.5"
        >
          <UBadge :color="statusColor(check.status)" variant="subtle" size="sm" class="w-6 h-6 flex items-center justify-center rounded-full flex-shrink-0 font-bold text-xs mt-0.5">
            {{ statusIcon(check.status) }}
          </UBadge>
          <div class="flex flex-col gap-0.5 min-w-0">
            <span class="text-sm font-medium">{{ check.label }}</span>
            <span class="text-xs text-gray-500 break-all">{{ check.detail }}</span>
          </div>
        </div>
      </div>

      <!-- Image issues -->
      <div v-if="data.image_issues.length" class="flex flex-col gap-2">
        <p class="text-sm font-semibold text-gray-700">Image alt issues ({{ data.image_issues.length }})</p>
        <div class="flex flex-col gap-1.5">
          <div v-for="(issue, i) in data.image_issues" :key="i" class="flex items-start gap-2.5 bg-gray-50 rounded-lg px-3 py-2">
            <UBadge :color="issue.issue === 'missing_alt' ? 'error' : 'warning'" variant="subtle" size="sm" class="w-5 h-5 flex items-center justify-center rounded-full flex-shrink-0 font-bold text-xs mt-0.5">
              {{ issue.issue === 'missing_alt' ? '✗' : '!' }}
            </UBadge>
            <div class="flex flex-col gap-0.5 min-w-0">
              <span class="text-sm font-medium">{{ issue.issue === 'missing_alt' ? 'Missing alt' : 'Empty alt' }}</span>
              <span class="text-xs text-gray-500 break-all">{{ issue.src || '(no src)' }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Heading issues -->
      <div v-if="data.heading_issues.length" class="flex flex-col gap-2">
        <p class="text-sm font-semibold text-gray-700">Heading issues</p>
        <div class="flex flex-col gap-1.5">
          <div v-for="(issue, i) in data.heading_issues" :key="i" class="flex items-start gap-2.5 bg-gray-50 rounded-lg px-3 py-2">
            <UBadge color="warning" variant="subtle" size="sm" class="w-5 h-5 flex items-center justify-center rounded-full flex-shrink-0 font-bold text-xs mt-0.5">!</UBadge>
            <div class="flex flex-col gap-0.5 min-w-0">
              <span class="text-sm font-medium">{{ issue.tag.toUpperCase() }}: {{ issue.issue }}</span>
              <span v-if="issue.text" class="text-xs text-gray-500">"{{ issue.text }}"</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Form issues -->
      <div v-if="data.form_issues.length" class="flex flex-col gap-2">
        <p class="text-sm font-semibold text-gray-700">Form label issues ({{ data.form_issues.length }})</p>
        <div class="flex flex-col gap-1.5">
          <div v-for="(issue, i) in data.form_issues" :key="i" class="flex items-start gap-2.5 bg-gray-50 rounded-lg px-3 py-2">
            <UBadge color="error" variant="subtle" size="sm" class="w-5 h-5 flex items-center justify-center rounded-full flex-shrink-0 font-bold text-xs mt-0.5">✗</UBadge>
            <div class="flex flex-col gap-0.5 min-w-0">
              <span class="text-sm font-medium">
                {{ issue.element }}<span v-if="issue.input_type"> [type="{{ issue.input_type }}"]</span>
              </span>
              <span class="text-xs text-gray-500">{{ issue.issue }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- ARIA stats -->
      <div class="flex flex-col gap-2">
        <p class="text-sm font-semibold text-gray-700">ARIA usage</p>
        <div class="flex gap-3 flex-wrap">
          <div class="bg-primary-50 border border-primary-100 rounded-lg px-4 py-3 flex flex-col gap-0.5 min-w-[90px] text-center">
            <span class="text-2xl font-bold text-primary-600">{{ data.aria_roles_count }}</span>
            <span class="text-xs text-gray-500">ARIA roles</span>
          </div>
          <div class="bg-primary-50 border border-primary-100 rounded-lg px-4 py-3 flex flex-col gap-0.5 min-w-[90px] text-center">
            <span class="text-2xl font-bold text-primary-600">{{ data.aria_labels_count }}</span>
            <span class="text-xs text-gray-500">aria-label attrs</span>
          </div>
          <div class="bg-primary-50 border border-primary-100 rounded-lg px-4 py-3 flex flex-col gap-0.5 min-w-[90px] text-center">
            <span class="text-2xl font-bold text-primary-600">{{ data.aria_landmarks.length }}</span>
            <span class="text-xs text-gray-500">Landmarks</span>
          </div>
        </div>
      </div>
    </div>
  </UCard>
</template>
