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
      status: d.hsts.present ? 'pass' : (d.https ? 'warn' : 'fail') as Status,
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
  const passed = headerChecks.value.filter(h => h.status === 'pass').length
  return Math.round((passed / headerChecks.value.length) * 100)
})

const scoreStatus = computed<Status>(() => {
  if (score.value >= 80) return 'pass'
  if (score.value >= 50) return 'warn'
  return 'fail'
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
</script>

<template>
  <UCard>
    <template #header>
      <div class="flex items-center gap-2">
        <UIcon name="i-heroicons-lock-closed" class="w-5 h-5 text-primary-500" />
        <h2 class="text-lg font-bold">Security</h2>
      </div>
    </template>

    <div class="flex flex-col gap-6">
      <!-- Score ring -->
      <div class="flex items-center gap-5">
        <div
          class="w-20 h-20 rounded-full border-[5px] flex flex-col items-center justify-center flex-shrink-0"
          :class="ringClass(scoreStatus)"
        >
          <span class="text-xl font-bold leading-none">{{ score }}</span>
          <span class="text-xs text-gray-400">/ 100</span>
        </div>
        <div>
          <p class="font-semibold">Security score</p>
          <p class="text-sm text-gray-400 mt-0.5">Based on HTTPS &amp; security headers</p>
        </div>
      </div>

      <!-- Header checks -->
      <div class="flex flex-col gap-2">
        <p class="text-sm font-semibold text-gray-700">Security headers</p>
        <div
          v-for="row in headerChecks"
          :key="row.label"
          class="flex items-start gap-3 bg-gray-50 rounded-lg px-3 py-2.5"
        >
          <UBadge :color="statusColor(row.status)" variant="subtle" size="sm" class="w-6 h-6 flex items-center justify-center rounded-full flex-shrink-0 font-bold text-xs mt-0.5">
            {{ statusIcon(row.status) }}
          </UBadge>
          <div class="flex flex-col gap-0.5 min-w-0">
            <span class="text-sm font-medium">{{ row.label }}</span>
            <span v-if="row.check.value" class="text-xs text-gray-500 break-all">{{ row.check.value }}</span>
            <span v-else-if="!row.check.present" class="text-xs text-gray-400">Not set</span>
          </div>
        </div>
      </div>

      <!-- Mixed content -->
      <div class="flex flex-col gap-2">
        <div class="flex items-center gap-2">
          <p class="text-sm font-semibold text-gray-700">Mixed content</p>
          <UBadge :color="data.mixed_content_count === 0 ? 'success' : 'error'" variant="subtle" size="sm">
            {{ data.mixed_content_count === 0 ? '✓ None' : `✗ ${data.mixed_content_count} found` }}
          </UBadge>
        </div>
        <ul v-if="data.mixed_content_urls.length" class="flex flex-col gap-1">
          <li
            v-for="url in data.mixed_content_urls"
            :key="url"
            class="text-xs font-mono text-red-700 bg-red-50 px-2 py-1 rounded break-all"
          >
            {{ url }}
          </li>
        </ul>
      </div>

      <!-- Server disclosure -->
      <div v-if="data.server_header || data.x_powered_by" class="flex flex-col gap-2">
        <p class="text-sm font-semibold text-gray-700">Server disclosure</p>
        <div class="flex flex-col gap-2">
          <div v-if="data.server_header" class="flex gap-3 text-sm">
            <span class="font-medium text-gray-500 w-28 flex-shrink-0">Server</span>
            <span class="text-amber-700 break-all">{{ data.server_header }}</span>
          </div>
          <div v-if="data.x_powered_by" class="flex gap-3 text-sm">
            <span class="font-medium text-gray-500 w-28 flex-shrink-0">X-Powered-By</span>
            <span class="text-amber-700 break-all">{{ data.x_powered_by }}</span>
          </div>
        </div>
        <p class="text-xs text-gray-400">Exposing server software can aid attackers. Consider removing these headers.</p>
      </div>

      <!-- Cookies -->
      <div v-if="data.cookies.length" class="flex flex-col gap-2">
        <p class="text-sm font-semibold text-gray-700">Cookies ({{ data.cookies.length }})</p>
        <div class="overflow-x-auto">
          <table class="w-full text-sm border-collapse">
            <thead>
              <tr class="border-b-2 border-gray-100">
                <th class="text-left py-2 pr-4 font-semibold text-gray-500">Name</th>
                <th class="text-left py-2 pr-4 font-semibold text-gray-500">Secure</th>
                <th class="text-left py-2 pr-4 font-semibold text-gray-500">HttpOnly</th>
                <th class="text-left py-2 font-semibold text-gray-500">SameSite</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="cookie in data.cookies" :key="cookie.name" class="border-b border-gray-50 last:border-0">
                <td class="py-1.5 pr-4 font-medium">{{ cookie.name }}</td>
                <td class="py-1.5 pr-4">
                  <span :class="cookie.secure ? 'text-green-700 font-bold' : 'text-red-700 font-bold'">
                    {{ cookie.secure ? '✓' : '✗' }}
                  </span>
                </td>
                <td class="py-1.5 pr-4">
                  <span :class="cookie.http_only ? 'text-green-700 font-bold' : 'text-red-700 font-bold'">
                    {{ cookie.http_only ? '✓' : '✗' }}
                  </span>
                </td>
                <td class="py-1.5 text-gray-600">{{ cookie.same_site ?? '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </UCard>
</template>
