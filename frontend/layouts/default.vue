<template>
  <div class="layout">
    <!-- Header -->
    <header class="header glass">
      <div class="container header__inner">
        <NuxtLink to="/" class="header__logo">
          <span class="header__logo-icon">⚡</span>
          <span class="header__logo-text">Khudyakov<span class="text-gradient">Inc.</span></span>
        </NuxtLink>

        <button class="header__burger" @click="menuOpen = !menuOpen" :class="{ active: menuOpen }">
          <span></span>
          <span></span>
          <span></span>
        </button>

        <nav class="header__nav" :class="{ open: menuOpen }">
          <NuxtLink to="/" class="header__link" @click="menuOpen = false">Главная</NuxtLink>
          <NuxtLink to="/services" class="header__link" @click="menuOpen = false">Услуги</NuxtLink>
          <NuxtLink to="/portfolio" class="header__link" @click="menuOpen = false">Портфолио</NuxtLink>
          <NuxtLink to="/admin" class="header__link header__link--admin" @click="menuOpen = false">Админка</NuxtLink>
        </nav>
      </div>
    </header>

    <!-- Main content -->
    <main class="main">
      <slot />
    </main>

    <!-- Footer -->
    <footer class="footer">
      <div class="container footer__inner">
        <div class="footer__brand">
          <span class="header__logo-icon">⚡</span>
          <span class="header__logo-text">Khudyakov<span class="text-gradient">Inc.</span></span>
          <p class="footer__desc">Создаём цифровые продукты, которые решают бизнес-задачи.</p>
        </div>
        <div class="footer__copy">
          &copy; {{ new Date().getFullYear() }} Khudyakov Inc. Все права защищены.
        </div>
      </div>
    </footer>

    <!-- Chat Widget -->
    <ChatWidget />
  </div>
</template>

<script setup>
const menuOpen = ref(false)
</script>

<style scoped>
.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main {
  flex: 1;
  padding-top: 80px;
}

/* ── Header ──────────────────────────────── */
.header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  height: 80px;
  border-bottom: 1px solid var(--c-border);
}

.header__inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
}

.header__logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  color: var(--c-text-primary);
}

.header__logo-icon {
  font-size: 1.5rem;
}

.header__logo-text {
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.header__nav {
  display: flex;
  align-items: center;
  gap: var(--space-lg);
}

.header__link {
  color: var(--c-text-secondary);
  font-weight: 500;
  font-size: 0.95rem;
  transition: color var(--duration-fast) var(--ease-out);
  position: relative;
}

.header__link::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 0;
  width: 0;
  height: 2px;
  background: var(--c-gradient-1);
  border-radius: var(--radius-full);
  transition: width var(--duration-normal) var(--ease-out);
}

.header__link:hover,
.header__link.router-link-active {
  color: var(--c-text-primary);
}

.header__link:hover::after,
.header__link.router-link-active::after {
  width: 100%;
}

.header__link--admin {
  opacity: 0.5;
  font-size: 0.85rem;
}

.header__burger {
  display: none;
  flex-direction: column;
  gap: 5px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
}

.header__burger span {
  width: 24px;
  height: 2px;
  background: var(--c-text-primary);
  border-radius: var(--radius-full);
  transition: all var(--duration-fast) var(--ease-out);
}

.header__burger.active span:nth-child(1) {
  transform: rotate(45deg) translateY(5px);
}

.header__burger.active span:nth-child(2) {
  opacity: 0;
}

.header__burger.active span:nth-child(3) {
  transform: rotate(-45deg) translateY(-5px);
}

/* ── Footer ──────────────────────────────── */
.footer {
  border-top: 1px solid var(--c-border);
  padding: var(--space-3xl) 0 var(--space-xl);
}

.footer__inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: var(--space-lg);
}

.footer__brand {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-sm);
}

.footer__desc {
  color: var(--c-text-secondary);
  font-size: 0.9rem;
  margin-top: var(--space-xs);
}

.footer__copy {
  color: var(--c-text-muted);
  font-size: 0.8rem;
}

/* ── Responsive ──────────────────────────── */
@media (max-width: 768px) {
  .header__burger {
    display: flex;
  }

  .header__nav {
    position: fixed;
    top: 80px;
    left: 0;
    right: 0;
    bottom: 0;
    background: var(--c-bg-primary);
    flex-direction: column;
    justify-content: flex-start;
    padding-top: var(--space-3xl);
    gap: var(--space-xl);
    transform: translateX(100%);
    transition: transform var(--duration-normal) var(--ease-out);
  }

  .header__nav.open {
    transform: translateX(0);
  }

  .header__link {
    font-size: 1.2rem;
  }
}
</style>
