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
  <div class="page">
    <div class="page-header">
      <h1 class="page-title">Saved Reports</h1>
      <NuxtLink to="/" class="new-btn">+ New analysis</NuxtLink>
    </div>

    <div v-if="!reports?.length" class="empty">
      No reports saved yet. Run an analysis and click <strong>Save report</strong>.
    </div>

    <div v-else class="report-list">
      <div v-for="report in reports" :key="report.id" class="report-row">
        <div class="report-info">
          <NuxtLink :to="`/reports/${report.id}`" class="report-url">
            {{ report.url }}
          </NuxtLink>
          <span class="report-date">{{ formatDate(report.created_at) }}</span>
        </div>
        <div class="report-actions">
          <NuxtLink :to="`/reports/${report.id}`" class="view-btn">View</NuxtLink>
          <button class="delete-btn" @click="deleteReport(report.id)">Delete</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
}

.new-btn {
  padding: 0.5rem 1rem;
  background: #4f46e5;
  color: #fff;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  text-decoration: none;
  transition: background 0.15s;
}

.new-btn:hover { background: #4338ca; }

.empty {
  background: #fff;
  border-radius: 12px;
  padding: 3rem;
  text-align: center;
  color: #aaa;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.report-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.report-row {
  background: #fff;
  border-radius: 10px;
  padding: 1rem 1.25rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.07);
  transition: box-shadow 0.15s;
}

.report-row:hover { box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); }

.report-info {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  min-width: 0;
}

.report-url {
  font-weight: 600;
  color: #4f46e5;
  text-decoration: none;
  font-size: 0.95rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.report-url:hover { text-decoration: underline; }

.report-date {
  font-size: 0.78rem;
  color: #999;
}

.report-actions {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
}

.view-btn {
  padding: 0.35rem 0.85rem;
  background: #ede9fe;
  color: #4f46e5;
  border-radius: 6px;
  font-size: 0.82rem;
  font-weight: 600;
  text-decoration: none;
  transition: background 0.15s;
}

.view-btn:hover { background: #ddd6fe; }

.delete-btn {
  padding: 0.35rem 0.85rem;
  background: #fff1f2;
  color: #be123c;
  border: none;
  border-radius: 6px;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}

.delete-btn:hover { background: #ffe4e6; }
</style>
