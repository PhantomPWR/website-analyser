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

function ringClass(s: Status) {
  return s === 'pass' ? 'border-green-500' : s === 'warn' ? 'border-amber-500' : 'border-red-500'
}

function gradeClass(s: Status) {
  return s === 'pass' ? 'text-green-700' : s === 'warn' ? 'text-amber-700' : 'text-red-700'
}

function statBorderClass(s?: Status) {
  if (!s) return 'border-gray-200'
  return s === 'pass' ? 'border-green-500' : s === 'warn' ? 'border-amber-500' : 'border-red-500'
}

function statusColor(s: Status) {
  return s === 'pass' ? 'success' : s === 'warn' ? 'warning' : 'error'
}

function statusIcon(s: Status) {
  return s === 'pass' ? '✓' : s === 'warn' ? '!' : '✗'
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
  { label: 'Internal links', value: props.data.internal_links_total.toLocaleString() },
  { label: 'External links', value: props.data.external_links_total.toLocaleString() },
  {
    label: 'Broken links',
    value: props.data.broken_links.length.toLocaleString(),
    sub: `of ${props.data.internal_links_checked} checked`,
    status: props.data.broken_links.length === 0 ? 'pass' : 'fail',
  },
])

const readStatus = computed(() => readabilityStatus(props.data.flesch_reading_ease))
</script>

<template>
  <UCard>
    <template #header>
      <div class="flex items-center gap-2">
        <UIcon name="i-heroicons-pencil-square" class="w-5 h-5 text-primary-500" />
        <h2 class="text-lg font-bold">Content</h2>
      </div>
    </template>

    <div class="flex flex-col gap-6">
      <!-- Readability -->
      <div class="flex items-center gap-5">
        <div
          class="w-20 h-20 rounded-full border-[5px] flex flex-col items-center justify-center flex-shrink-0"
          :class="ringClass(readStatus)"
        >
          <span class="text-xl font-bold leading-none">{{ data.flesch_reading_ease }}</span>
          <span class="text-xs text-gray-400">/ 100</span>
        </div>
        <div>
          <p class="font-semibold">Flesch Reading Ease</p>
          <p class="text-sm font-semibold mt-0.5" :class="gradeClass(readStatus)">{{ data.readability_label }}</p>
          <p class="text-xs text-gray-400 mt-0.5">60–70 is considered ideal for general audiences</p>
        </div>
      </div>

      <!-- Content stats -->
      <div class="flex flex-col gap-3">
        <p class="text-sm font-semibold text-gray-700">Content stats</p>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div
            v-for="stat in stats"
            :key="stat.label"
            class="bg-gray-50 rounded-lg p-3 border-l-4 flex flex-col gap-0.5"
            :class="statBorderClass(stat.status)"
          >
            <span class="text-2xl font-bold text-gray-900">{{ stat.value }}</span>
            <span class="text-xs font-semibold text-gray-600">{{ stat.label }}</span>
            <span v-if="stat.sub" class="text-xs text-gray-400">{{ stat.sub }}</span>
          </div>
        </div>
      </div>

      <!-- Links -->
      <div class="flex flex-col gap-3">
        <p class="text-sm font-semibold text-gray-700">Links</p>
        <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
          <div
            v-for="stat in linkStats"
            :key="stat.label"
            class="bg-gray-50 rounded-lg p-3 border-l-4 flex flex-col gap-0.5"
            :class="statBorderClass(stat.status)"
          >
            <span class="text-2xl font-bold text-gray-900">{{ stat.value }}</span>
            <span class="text-xs font-semibold text-gray-600">{{ stat.label }}</span>
            <span v-if="stat.sub" class="text-xs text-gray-400">{{ stat.sub }}</span>
          </div>
        </div>

        <div v-if="data.broken_links.length" class="flex flex-col gap-1.5 mt-1">
          <div
            v-for="link in data.broken_links"
            :key="link.url"
            class="flex items-baseline gap-2 bg-red-50 rounded-lg px-3 py-2 text-sm"
          >
            <UBadge color="error" variant="subtle" size="sm" class="flex-shrink-0 font-bold">
              {{ link.status_code ?? 'ERR' }}
            </UBadge>
            <span class="text-red-700 break-all flex-1">{{ link.url }}</span>
            <span v-if="link.error" class="text-gray-400 text-xs whitespace-nowrap">{{ link.error }}</span>
          </div>
        </div>
      </div>

      <!-- Misc checks -->
      <div class="flex flex-col gap-2">
        <p class="text-sm font-semibold text-gray-700">Misc checks</p>
        <div class="flex flex-col gap-2">
          <div class="flex items-center gap-3 bg-gray-50 rounded-lg px-3 py-2.5">
            <UBadge :color="data.has_favicon ? 'success' : 'warning'" variant="subtle" size="sm" class="w-6 h-6 flex items-center justify-center rounded-full flex-shrink-0 font-bold text-xs">
              {{ data.has_favicon ? '✓' : '!' }}
            </UBadge>
            <span class="text-sm font-medium w-36 flex-shrink-0">Favicon</span>
            <span class="text-xs text-gray-500">{{ data.has_favicon ? 'Found' : 'Not found' }}</span>
          </div>
          <div class="flex items-center gap-3 bg-gray-50 rounded-lg px-3 py-2.5">
            <UBadge :color="data.has_meta_viewport ? 'success' : 'error'" variant="subtle" size="sm" class="w-6 h-6 flex items-center justify-center rounded-full flex-shrink-0 font-bold text-xs">
              {{ data.has_meta_viewport ? '✓' : '✗' }}
            </UBadge>
            <span class="text-sm font-medium w-36 flex-shrink-0">Meta viewport</span>
            <span class="text-xs text-gray-500">{{ data.has_meta_viewport ? 'Present' : 'Missing — required for mobile' }}</span>
          </div>
        </div>
      </div>

      <!-- Text preview -->
      <div v-if="data.text_preview" class="flex flex-col gap-2">
        <p class="text-sm font-semibold text-gray-700">Content preview</p>
        <p class="text-sm text-gray-500 leading-relaxed bg-gray-50 rounded-lg px-4 py-3 border-l-4 border-gray-200">
          {{ data.text_preview }}
        </p>
      </div>
    </div>
  </UCard>
</template>
