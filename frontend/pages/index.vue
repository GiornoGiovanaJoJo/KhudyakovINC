<template>
  <div>
    <!-- Hero Section -->
    <section class="hero">
      <div class="hero__bg"></div>
      <div class="container hero__content">
        <div class="hero__badge">🚀 Команда профессионалов</div>
        <h1 class="hero__title">
          Превращаем идеи <br />
          в <span class="text-gradient">цифровые продукты</span>
        </h1>
        <p class="hero__subtitle">
          Веб-разработка, мобильные приложения, UI/UX дизайн и IT-консалтинг.
          Полный цикл: от идеи до запуска.
        </p>
        <div class="hero__actions">
          <NuxtLink to="/portfolio" class="btn btn-primary">Наши работы</NuxtLink>
          <NuxtLink to="/services" class="btn btn-outline">Услуги</NuxtLink>
        </div>

        <div class="hero__stats">
          <div class="hero__stat">
            <div class="hero__stat-value">50+</div>
            <div class="hero__stat-label">Проектов</div>
          </div>
          <div class="hero__stat">
            <div class="hero__stat-value">5+</div>
            <div class="hero__stat-label">Лет опыта</div>
          </div>
          <div class="hero__stat">
            <div class="hero__stat-value">30+</div>
            <div class="hero__stat-label">Довольных клиентов</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Team Section -->
    <section class="section" id="team">
      <div class="container">
        <h2 class="section__title">Наша команда</h2>
        <p class="section__subtitle">
          Профессионалы, которые создают ваш продукт
        </p>

        <div class="grid-3" v-if="team.length">
          <TeamCard
            v-for="member in team"
            :key="member.id"
            :member="member"
            @select="selectedMember = member"
          />
        </div>

        <p v-else class="text-center" style="color: var(--c-text-muted)">
          Загрузка команды...
        </p>
      </div>
    </section>

    <!-- Team Modal -->
    <TeamModal
      v-if="selectedMember"
      :member="selectedMember"
      @close="selectedMember = null"
    />

    <!-- CTA Section -->
    <section class="cta section">
      <div class="container text-center">
        <h2 class="section__title">Готовы обсудить проект?</h2>
        <p class="section__subtitle mb-xl">
          Расскажите о вашей задаче в чате — наш ИИ-консультант ответит мгновенно
          и поможет подготовить коммерческое предложение.
        </p>
        <button class="btn btn-primary" @click="openChat">💬 Начать диалог</button>
      </div>
    </section>
  </div>
</template>

<script setup>
useHead({
  title: 'Khudyakov Inc. — Веб-разработка, дизайн и IT-решения',
})

const selectedMember = ref(null)
const team = ref([])

// Use lazy fetch to avoid blocking navigation and ensure client-side rendering
const { data, refresh } = await useFetch('/api/team/', {
  lazy: true,
  server: false // Ensure it runs on client for consistent behavior if server-side state is stale
})

watch(data, (newData) => {
  if (newData) {
    team.value = newData
  }
}, { immediate: true })

// Force refresh on mount just in case
onMounted(() => {
  if (!team.value.length) {
    refresh()
  }
})

const openChat = () => {
  const toggle = document.getElementById('chat-toggle')
  if (toggle) toggle.click()
}
</script>

<style scoped>
/* ── Hero ──────────────────────────────────── */
.hero {
  position: relative;
  padding: var(--space-4xl) 0;
  min-height: 85vh;
  display: flex;
  align-items: center;
  overflow: hidden;
}

.hero__bg {
  position: absolute;
  inset: 0;
  background: var(--c-gradient-hero);
  z-index: 0;
}

.hero__bg::after {
  content: '';
  position: absolute;
  top: 20%;
  left: 50%;
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, var(--c-accent-glow) 0%, transparent 70%);
  transform: translateX(-50%);
  filter: blur(80px);
  opacity: 0.5;
}

.hero__content {
  position: relative;
  z-index: 1;
  text-align: center;
  max-width: 800px;
}

.hero__badge {
  display: inline-block;
  padding: 0.4rem 1rem;
  background: var(--c-bg-glass);
  border: 1px solid var(--c-border);
  border-radius: var(--radius-full);
  font-size: 0.85rem;
  color: var(--c-text-secondary);
  margin-bottom: var(--space-xl);
  animation: fadeIn 0.6s var(--ease-out);
}

.hero__title {
  font-size: 3.5rem;
  font-weight: 900;
  line-height: 1.1;
  letter-spacing: -0.03em;
  margin-bottom: var(--space-xl);
  animation: slideUp 0.8s var(--ease-out);
}

.hero__subtitle {
  font-size: 1.15rem;
  color: var(--c-text-secondary);
  max-width: 560px;
  margin: 0 auto var(--space-2xl);
  line-height: 1.7;
  animation: slideUp 0.8s var(--ease-out) 0.1s both;
}

.hero__actions {
  display: flex;
  gap: var(--space-md);
  justify-content: center;
  margin-bottom: var(--space-4xl);
  animation: slideUp 0.8s var(--ease-out) 0.2s both;
}

.hero__stats {
  display: flex;
  justify-content: center;
  gap: var(--space-3xl);
  animation: fadeIn 1s var(--ease-out) 0.5s both;
}

.hero__stat {
  text-align: center;
}

.hero__stat-value {
  font-size: 2rem;
  font-weight: 800;
  background: var(--c-gradient-1);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero__stat-label {
  font-size: 0.85rem;
  color: var(--c-text-muted);
  margin-top: var(--space-xs);
}

/* ── CTA ──────────────────────────────────── */
.cta {
  background: var(--c-gradient-hero);
  border-top: 1px solid var(--c-border);
  border-bottom: 1px solid var(--c-border);
}

/* ── Responsive ───────────────────────────── */
@media (max-width: 768px) {
  .hero {
    min-height: auto;
    padding: var(--space-3xl) 0;
  }

  .hero__title {
    font-size: 2.2rem;
  }

  .hero__stats {
    gap: var(--space-xl);
  }

  .hero__stat-value {
    font-size: 1.5rem;
  }

  .hero__actions {
    flex-direction: column;
    align-items: center;
  }
}
</style>
