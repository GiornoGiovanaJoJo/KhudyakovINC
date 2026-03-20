<template>
  <div class="layout" @mousemove="onGlobalMouseMove">
    <!-- Header -->
    <header class="header glass" :class="{ 'header--scrolled': isScrolled }">
      <div class="container header__inner">
        <NuxtLink to="/" class="header__logo">
          <img src="/images/logo.png" alt="Logo" class="header__logo-img">
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
            <div class="header__auth">
              <template v-if="isLoggedIn && user">
                <span class="header__user-name">{{ user.full_name || 'Профиль' }}</span>
                <button @click="handleLogout" class="header__logout-btn">Выход</button>
              </template>
              <NuxtLink v-else-if="isLoggedIn" to="/profile" class="header__link" @click="menuOpen = false">Профиль</NuxtLink>
              <NuxtLink v-else to="/auth/login" class="header__link" @click="menuOpen = false">Вход</NuxtLink>
            </div>
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
        <div class="footer__grid">
          <!-- Brand -->
          <div class="footer__brand">
            <NuxtLink to="/" class="header__logo mb-sm">
              <img src="/images/logo.png" alt="Logo" class="header__logo-img">
              <span class="header__logo-text">Khudyakov<span class="text-gradient">Inc.</span></span>
            </NuxtLink>
            <p class="footer__desc" style="text-align: left; max-width: 300px;">
              Создаём премиальные цифровые продукты, которые помогают вашему бизнесу расти и выделяться на рынке.
            </p>
          </div>

          <!-- Navigation -->
          <div class="footer__col">
            <h4 class="footer__col-title">Навигация</h4>
            <ul class="footer__links">
              <li><NuxtLink to="/" class="footer__link">Главная</NuxtLink></li>
              <li><NuxtLink to="/services" class="footer__link">Услуги</NuxtLink></li>
              <li><NuxtLink to="/portfolio" class="footer__link">Портфолио</NuxtLink></li>
            </ul>
          </div>

          <!-- Services -->
          <div class="footer__col">
            <h4 class="footer__col-title">Услуги</h4>
            <ul class="footer__links">
              <li><a href="#" class="footer__link">Веб-разработка</a></li>
              <li><a href="#" class="footer__link">Сложные сервисы</a></li>
              <li><a href="#" class="footer__link">UI/UX Дизайн</a></li>
              <li><a href="#" class="footer__link">IT-Консалтинг</a></li>
            </ul>
          </div>

          <!-- Contact -->
          <div class="footer__col">
            <h4 class="footer__col-title">Контакты</h4>
            <div class="footer__contact-item">
              <span>📍</span> г. Москва
            </div>
            <div class="footer__contact-item">
              <span>📧</span> kbootovsk@gmail.com
            </div>
            <div class="footer__contact-item">
              <span>📞</span> +7 (993) 338-31-45
            </div>
          </div>
        </div>

        <div class="footer__bottom" style="margin-top: var(--space-3xl); padding-top: var(--space-xl); border-top: 1px solid var(--c-border); width: 100%;">
          <div class="footer__copy">
            &copy; {{ new Date().getFullYear() }} Khudyakov Inc. Все права защищены.
          </div>
        </div>
      </div>
    </footer>

    <!-- Chat Widget -->
    <ChatWidget />

    <!-- Scroll-to-top Button -->
    <button
      class="scroll-top-btn"
      :class="{ 'scroll-top-btn--visible': showScrollTop }"
      @click="scrollToTop"
      aria-label="Наверх"
    >
      ↑
    </button>

    <!-- Ambient Cursor Glow -->
    <div
      class="ambient-glow"
      :style="ambientGlowStyle"
    ></div>
  </div>
</template>

<script setup>
import { useHeaderShrink, useScrollToTop } from '~/composables/useAnimations'

const menuOpen = ref(false)
const isLoggedIn = ref(false)
const user = ref(null)

// Header shrink on scroll
const isScrolled = useHeaderShrink()

// Scroll-to-top button
const { showButton: showScrollTop, scrollToTop } = useScrollToTop()

// Check cookie or token on mount
onMounted(async () => {
  const token = localStorage.getItem('auth_token')
  isLoggedIn.value = !!token
  
  if (isLoggedIn.value) {
    try {
      user.value = await $fetch('/api/users/me', {
        headers: { Authorization: `Bearer ${token}` }
      })
    } catch (e) {
      console.warn("Failed to fetch user info", e)
      // Token might be invalid
      if (e.status === 401) {
        handleLogout()
      }
    }
  }
})

const handleLogout = () => {
  localStorage.removeItem('auth_token')
  isLoggedIn.value = false
  user.value = null
  navigateTo('/')
}

// Ambient cursor glow
const cursorPos = reactive({ x: -200, y: -200 })
const onGlobalMouseMove = (e) => {
  if (window.innerWidth < 768) return
  cursorPos.x = e.clientX
  cursorPos.y = e.clientY
}
const ambientGlowStyle = computed(() => ({
  left: `${cursorPos.x}px`,
  top: `${cursorPos.y}px`,
}))
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
  transition: padding-top 0.3s var(--ease-out);
}

/* Adjust padding when header shrinks */
.header--scrolled ~ .main {
  padding-top: 60px;
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
  transition: all 0.4s var(--ease-out);
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

.header__logo-img {
  height: 40px;
  width: auto;
  object-fit: contain;
  transition: height 0.3s var(--ease-out);
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

.header__auth {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.header__user-name {
  color: var(--c-text-primary);
  font-weight: 600;
  font-size: 0.9rem;
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.header__logout-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--c-border);
  color: var(--c-text-muted);
  padding: 0.3rem 0.6rem;
  border-radius: var(--radius-sm);
  font-size: 0.8rem;
  cursor: pointer;
  transition: all var(--duration-fast);
}

.header__logout-btn:hover {
  background: rgba(255, 77, 77, 0.1);
  color: #ff4d4d;
  border-color: rgba(255, 77, 77, 0.2);
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
    background: #0f0f12; /* Solid, opaque background */
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

/* ── Ambient Cursor Glow ─────────────────── */
.ambient-glow {
  position: fixed;
  width: 600px;
  height: 600px;
  border-radius: 50%;
  pointer-events: none;
  z-index: 0;
  transform: translate(-50%, -50%);
  background: radial-gradient(
    circle,
    rgba(108, 92, 231, 0.06) 0%,
    rgba(108, 92, 231, 0.03) 30%,
    transparent 70%
  );
  transition: left 0.3s ease-out, top 0.3s ease-out;
  will-change: left, top;
}

@media (max-width: 768px) {
  .ambient-glow {
    display: none;
  }
}
</style>
