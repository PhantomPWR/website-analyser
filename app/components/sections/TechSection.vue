<script setup lang="ts">
import type { TechResult } from '~/composables/useAnalyser'

const props = defineProps<{ data: TechResult }>()

const categoryOrder = [
  'CMS',
  'E-commerce',
  'JavaScript Framework',
  'JavaScript Library',
  'Static Site Generator',
  'UI Framework',
  'Analytics',
  'CDN',
  'Hosting',
  'Web Server',
  'Programming Language',
  'Font Service',
]

const sortedCategories = computed(() => {
  const keys = Object.keys(props.data.categories)
  return [
    ...categoryOrder.filter(c => keys.includes(c)),
    ...keys.filter(c => !categoryOrder.includes(c)),
  ]
})

function techsForCategory(cat: string) {
  return props.data.technologies.filter(t => t.category === cat)
}
</script>

<template>
  <section class="section-card">
    <h2 class="section-title">
      <span class="section-icon">🛠️</span> Technology Detection
    </h2>

    <div v-if="data.technologies.length === 0" class="empty">
      No technologies detected — the page may be static or heavily obfuscated.
    </div>

    <div v-else class="summary-bar">
      <span class="summary-count">{{ data.technologies.length }} technologies detected</span>
      <span class="summary-cats">across {{ sortedCategories.length }} categories</span>
    </div>

    <div v-for="cat in sortedCategories" :key="cat" class="category-block">
      <h3 class="category-title">{{ cat }}</h3>
      <div class="tech-grid">
        <div
          v-for="tech in techsForCategory(cat)"
          :key="tech.name"
          class="tech-card"
        >
          <span class="tech-icon">{{ tech.icon ?? '📦' }}</span>
          <div class="tech-info">
            <span class="tech-name">{{ tech.name }}</span>
            <span v-if="tech.version" class="tech-version">v{{ tech.version }}</span>
          </div>
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

.empty {
  color: #999;
  font-size: 0.9rem;
  padding: 1rem 0;
}

.summary-bar {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
}

.summary-count {
  font-size: 1.4rem;
  font-weight: 700;
  color: #4f46e5;
}

.summary-cats {
  font-size: 0.88rem;
  color: #888;
}

.category-block {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.category-title {
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #888;
}

.tech-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
}

.tech-card {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #f5f3ff;
  border: 1px solid #ede9fe;
  border-radius: 8px;
  padding: 0.5rem 0.85rem;
}

.tech-icon {
  font-size: 1.1rem;
  line-height: 1;
}

.tech-info {
  display: flex;
  flex-direction: column;
  gap: 0.05rem;
}

.tech-name {
  font-size: 0.88rem;
  font-weight: 600;
  color: #3730a3;
}

.tech-version {
  font-size: 0.72rem;
  color: #7c6fcd;
}
</style>
