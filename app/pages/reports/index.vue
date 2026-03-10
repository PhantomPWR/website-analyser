<script setup lang="ts">
const config = useRuntimeConfig()
const apiBase = config.public.apiBase

interface ReportMeta {
  id: string
  url: string
  created_at: string
}

const { data: reports, refresh } = await useAsyncData<ReportMeta[]>(
  'reports',
  () => $fetch(`${apiBase}/reports`),
  { server: false },
)

function formatDate(iso: string) {
  return new Date(iso).toLocaleString()
}

async function deleteReport(id: string) {
  await $fetch(`${apiBase}/reports/${id}`, { method: 'DELETE' })
  await refresh()
}
</script>

<template>
  <div class="flex flex-col gap-6">
    <div class="flex items-center justify-between gap-4">
      <h1 class="text-2xl font-bold text-gray-900">Saved Reports</h1>
      <UButton
        to="/"
        label="New analysis"
        icon="i-heroicons-plus"
        size="sm"
      />
    </div>

    <div v-if="!reports?.length" class="bg-white rounded-xl shadow-sm p-12 text-center text-gray-400 text-sm">
      No reports saved yet. Run an analysis and click <strong class="text-gray-600">Save report</strong>.
    </div>

    <div v-else class="flex flex-col gap-3">
      <UCard
        v-for="report in reports"
        :key="report.id"
        class="hover:shadow-md transition-shadow"
      >
        <div class="flex items-center justify-between gap-4">
          <div class="flex flex-col gap-1 min-w-0">
            <NuxtLink
              :to="`/reports/${report.id}`"
              class="font-semibold text-primary-600 hover:underline text-sm truncate"
            >
              {{ report.url }}
            </NuxtLink>
            <span class="text-xs text-gray-400">{{ formatDate(report.created_at) }}</span>
          </div>
          <div class="flex gap-2 flex-shrink-0">
            <UButton
              :to="`/reports/${report.id}`"
              label="View"
              size="xs"
              variant="subtle"
              color="primary"
            />
            <UButton
              label="Delete"
              size="xs"
              variant="subtle"
              color="error"
              @click="deleteReport(report.id)"
            />
          </div>
        </div>
      </UCard>
    </div>
  </div>
</template>
