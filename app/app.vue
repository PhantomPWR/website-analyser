<template>
  <div class="app">
    <header class="navbar">
      <div class="navbar-inner">
        <NuxtLink to="/" class="logo">
          <span class="logo-icon">🔍</span>
          <span class="logo-text">Website Analyser</span>
        </NuxtLink>
        <nav class="nav-links">
          <NuxtLink to="/reports" class="nav-link">Reports</NuxtLink>
        </nav>
      </div>
    </header>

    <main class="main">
      <NuxtRouteAnnouncer />
      <NuxtPage />
    </main>
  </div>
</template>

<style>
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #f5f7fa;
  color: #1a1a2e;
  min-height: 100vh;
}

.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar {
  background: #1a1a2e;
  padding: 0 1.5rem;
  height: 56px;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.navbar-inner {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.nav-links {
  display: flex;
  gap: 0.5rem;
}

.nav-link {
  color: rgba(255, 255, 255, 0.75);
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 500;
  padding: 0.3rem 0.75rem;
  border-radius: 6px;
  transition: color 0.15s, background 0.15s;
}

.nav-link:hover,
.nav-link.router-link-active {
  color: #fff;
  background: rgba(255, 255, 255, 0.1);
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  color: #fff;
  font-weight: 600;
  font-size: 1.1rem;
}

.logo-icon {
  font-size: 1.3rem;
}

.main {
  flex: 1;
  padding: 2rem 1.5rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}
</style>
