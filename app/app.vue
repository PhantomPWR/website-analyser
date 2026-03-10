<template>
  <UApp>
    <div class="min-h-screen flex flex-col bg-gray-50">
      <header class="bg-gray-900 shadow-md">
        <div class="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
          <NuxtLink to="/" class="flex items-center gap-2 text-white font-semibold text-lg no-underline">
            <UIcon name="i-heroicons-magnifying-glass-circle" class="w-6 h-6 text-primary-400" />
            Website Analyser
          </NuxtLink>
          <nav>
            <UButton
              to="/reports"
              label="Reports"
              variant="ghost"
              color="neutral"
              class="text-gray-300 hover:text-white"
            />
          </nav>
        </div>
      </header>

      <main class="flex-1 max-w-6xl mx-auto w-full px-6 py-8">
        <NuxtRouteAnnouncer />
        <NuxtPage />
      </main>
    </div>
  </UApp>
</template>
