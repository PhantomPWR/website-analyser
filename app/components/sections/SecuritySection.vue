<script setup lang="ts">
import type { CookieCheck, HeaderCheck, SecurityResult } from '~/composables/useAnalyser'

const props = defineProps<{ data: SecurityResult }>()

type Status = 'pass' | 'warn' | 'fail'

interface HeaderRow {
  label: string
  check: HeaderCheck
  status: Status
}

const headerChecks = computed<HeaderRow[]>(() => {
  const d = props.data
  return [
    {
      label: 'HTTPS',
      check: { present: d.https, value: null, note: null },
      status: d.https ? 'pass' : 'fail',
    },
    {
      label: 'Strict-Transport-Security (HSTS)',
      check: d.hsts,
      status: d.hsts.present ? 'pass' : (d.data?.https ? 'warn' : 'fail') as Status,
    },
    {
      label: 'Content-Security-Policy',
      check: d.csp,
      status: d.csp.present ? 'pass' : 'warn',
    },
    {
      label: 'X-Frame-Options',
      check: d.x_frame_options,
      status: d.x_frame_options.present ? 'pass' : 'warn',
    },
    {
      label: 'X-Content-Type-Options',
      check: d.x_content_type_options,
      status: d.x_content_type_options.present
        ? (d.x_content_type_options.value?.toLowerCase() === 'nosniff' ? 'pass' : 'warn')
        : 'warn',
    },
    {
      label: 'Referrer-Policy',
      check: d.referrer_policy,
      status: d.referrer_policy.present ? 'pass' : 'warn',
    },
    {
      label: 'Permissions-Policy',
      check: d.permissions_policy,
      status: d.permissions_policy.present ? 'pass' : 'warn',
    },
    {
      label: 'Cross-Origin-Opener-Policy',
      check: d.coop,
      status: d.coop.present ? 'pass' : 'warn',
    },
  ]
})

function cookieStatus(c: CookieCheck): Status {
  if (!c.secure || !c.http_only) return 'fail'
  if (!c.same_site) return 'warn'
  return 'pass'
}

const score = computed(() => {
  const total = headerChecks.value.length
  const passed = headerChecks.value.filter(h => h.status === 'pass').length
  return Math.round((passed / total) * 100)
})

const scoreStatus = computed<Status>(() => {
  if (score.value >= 80) return 'pass'
  if (score.value >= 50) return 'warn'
  return 'fail'
})
</script>

<template>
  <section class="section-card">
    <h2 class="section-title">
      <span class="section-icon">🔒</span> Security
    </h2>

    <!-- Score -->
    <div class="score-row">
      <div class="score-ring" :class="`ring--${scoreStatus}`">
        <span class="score-value">{{ score }}</span>
        <span class="score-label">/ 100</span>
      </div>
      <div class="score-meta">
        <p class="score-heading">Security score</p>
        <p class="score-sub">Based on HTTPS &amp; security headers</p>
      </div>
    </div>

    <!-- Header checks -->
    <div class="checks">
      <h3 class="block-title">Security headers</h3>
      <div
        v-for="row in headerChecks"
        :key="row.label"
        class="check-row"
      >
        <span class="check-badge" :class="`badge--${row.status}`">
          {{ row.status === 'pass' ? '✓' : row.status === 'warn' ? '!' : '✗' }}
        </span>
        <div class="check-body">
          <span class="check-label">{{ row.label }}</span>
          <span v-if="row.check.value" class="check-value">{{ row.check.value }}</span>
          <span v-else-if="!row.check.present" class="check-missing">Not set</span>
        </div>
      </div>
    </div>

    <!-- Mixed content -->
    <div class="block">
      <h3 class="block-title">
        Mixed content
        <span class="badge" :class="data.mixed_content_count === 0 ? 'badge--pass' : 'badge--fail'">
          {{ data.mixed_content_count === 0 ? '✓ None' : `✗ ${data.mixed_content_count} found` }}
        </span>
      </h3>
      <ul v-if="data.mixed_content_urls.length" class="url-list">
        <li v-for="url in data.mixed_content_urls" :key="url" class="url-item">{{ url }}</li>
      </ul>
    </div>

    <!-- Server info -->
    <div v-if="data.server_header || data.x_powered_by" class="block">
      <h3 class="block-title">Server disclosure</h3>
      <div class="info-rows">
        <div v-if="data.server_header" class="info-row">
          <span class="info-key">Server</span>
          <span class="info-val warn-text">{{ data.server_header }}</span>
        </div>
        <div v-if="data.x_powered_by" class="info-row">
          <span class="info-key">X-Powered-By</span>
          <span class="info-val warn-text">{{ data.x_powered_by }}</span>
        </div>
      </div>
      <p class="hint">Exposing server software can aid attackers. Consider removing these headers.</p>
    </div>

    <!-- Cookies -->
    <div v-if="data.cookies.length" class="block">
      <h3 class="block-title">Cookies ({{ data.cookies.length }})</h3>
      <table class="cookie-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Secure</th>
            <th>HttpOnly</th>
            <th>SameSite</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="cookie in data.cookies" :key="cookie.name" :class="`row--${cookieStatus(cookie)}`">
            <td class="cookie-name">{{ cookie.name }}</td>
            <td><span :class="cookie.secure ? 'flag--pass' : 'flag--fail'">{{ cookie.secure ? '✓' : '✗' }}</span></td>
            <td><span :class="cookie.http_only ? 'flag--pass' : 'flag--fail'">{{ cookie.http_only ? '✓' : '✗' }}</span></td>
            <td>{{ cookie.same_site ?? '—' }}</td>
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
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
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
  margin-top: 1px;
}

.badge--pass { background: #d1fae5; color: #065f46; }
.badge--warn { background: #fef3c7; color: #92400e; }
.badge--fail { background: #fee2e2; color: #991b1b; }

.badge {
  padding: 0.15rem 0.5rem;
  border-radius: 99px;
  font-size: 0.75rem;
  font-weight: 600;
}

.check-body {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  min-width: 0;
}

.check-label { font-weight: 500; font-size: 0.9rem; }
.check-value { font-size: 0.78rem; color: #555; word-break: break-all; }
.check-missing { font-size: 0.78rem; color: #aaa; }

.block { display: flex; flex-direction: column; }

.url-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.url-item {
  font-size: 0.82rem;
  font-family: monospace;
  color: #b91c1c;
  background: #fff1f2;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  word-break: break-all;
}

.info-rows { display: flex; flex-direction: column; gap: 0.4rem; margin-bottom: 0.5rem; }

.info-row {
  display: flex;
  gap: 1rem;
  align-items: baseline;
  font-size: 0.88rem;
}

.info-key { font-weight: 500; color: #555; min-width: 110px; }
.info-val { word-break: break-all; }
.warn-text { color: #92400e; }

.hint { font-size: 0.78rem; color: #888; }

.cookie-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}

.cookie-table th {
  text-align: left;
  padding: 0.4rem 0.75rem;
  font-weight: 600;
  color: #555;
  border-bottom: 2px solid #f0f0f0;
}

.cookie-table td {
  padding: 0.4rem 0.75rem;
  border-bottom: 1px solid #f9f9f9;
}

.cookie-name { font-weight: 500; }
.flag--pass { color: #065f46; font-weight: 700; }
.flag--fail { color: #991b1b; font-weight: 700; }
</style>
