<template>
  <div>
    <!-- Hero Section -->
    <section class="hero">
      <div class="hero__bg">
        <img src="/images/abstract_hero.png" alt="Abstract Background" class="hero__bg-img" />
      </div>
      <div class="container hero__content">
        <div class="hero__badge">🚀 Команда профессионалов</div>
        <h1 class="hero__title">
          Превращаем идеи <br />
          в <span class="text-gradient">цифровые продукты</span>
        </h1>
        <p class="hero__subtitle">
          Веб-разработка, дизайн и IT-консалтинг.
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

    <!-- Services Overview -->
    <section class="section">
      <div class="container">
        <h2 class="section__title">Что мы умеем</h2>
        <p class="section__subtitle">
          Мы предлагаем комплексные решения для запуска и развития вашего бизнеса в цифровой среде.
        </p>
        <div class="grid-3">
          <ServiceCard
            v-for="service in topServices"
            :key="service.id"
            :service="service"
          />
        </div>
        <div class="text-center mt-xl">
          <NuxtLink to="/services" class="btn btn-outline">Посмотреть все услуги</NuxtLink>
        </div>
      </div>
    </section>

    <!-- Portfolio Highlights -->
    <section class="section" style="background: var(--c-bg-secondary)">
      <div class="container">
        <h2 class="section__title">Наши работы</h2>
        <p class="section__subtitle">
          Проекты, которыми мы гордимся. Каждый из них — это уникальное решение сложной задачи.
        </p>
        <div class="grid-3" v-if="portfolio.length">
          <PortfolioCard
            v-for="project in portfolio.slice(0, 3)"
            :key="project.id"
            :project="project"
          />
        </div>
        <div class="text-center mt-xl">
          <NuxtLink to="/portfolio" class="btn btn-outline">Весь портфель</NuxtLink>
        </div>
      </div>
    </section>

    <!-- How We Work -->
    <section class="section">
      <div class="container">
        <h2 class="section__title">Как мы работаем</h2>
        <p class="section__subtitle">
          Наш процесс прозрачен и эффективен. Мы сопровождаем вас на каждом этапе создания продукта.
        </p>
        <div class="process-grid">
          <div class="process-step">
            <div class="process-step__number">01</div>
            <h3 class="process-step__title">Аналитика</h3>
            <p class="process-step__desc">Погружаемся в ваш бизнес, определяем цели и требования.</p>
          </div>
          <div class="process-step">
            <div class="process-step__number">02</div>
            <h3 class="process-step__title">Дизайн</h3>
            <p class="process-step__desc">Создаем удобные и современные интерфейсы (UI/UX).</p>
          </div>
          <div class="process-step">
            <div class="process-step__number">03</div>
            <h3 class="process-step__title">Разработка</h3>
            <p class="process-step__desc">Пишем чистый код, используя передовой стек технологий.</p>
          </div>
          <div class="process-step">
            <div class="process-step__number">04</div>
            <h3 class="process-step__title">Запуск</h3>
            <p class="process-step__desc">Тестируем и выводим проект на рынок, обеспечивая поддержку.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Team Section -->
    <section class="section" id="team" style="background: var(--c-bg-secondary)">
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

    <!-- FAQ Section -->
    <section class="section">
      <div class="container">
        <h2 class="section__title">Часто задаваемые вопросы</h2>
        <div class="faq-list">
          <div class="faq-item">
            <h3 class="faq-item__question">Сколько времени занимает разработка?</h3>
            <p class="faq-item__answer">Сроки зависят от сложности проекта. Корпоративный сайт — от 2 недель, сложный сервис или CRM — от 1.5 месяцев.</p>
          </div>
          <div class="faq-item">
            <h3 class="faq-item__question">Какие технологии вы используете?</h3>
            <p class="faq-item__answer">Мы работаем с современным стеком: Vue.js/Nuxt.js, React, Node.js, Python (FastAPI/Django), PostgreSQL и Docker.</p>
          </div>
          <div class="faq-item">
            <h3 class="faq-item__question">Оказываете ли вы поддержку после запуска?</h3>
            <p class="faq-item__answer">Да, мы предлагаем гарантийное обслуживание в течение года и услуги по развитию вашего продукта.</p>
          </div>
        </div>
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
const portfolio = ref([])
const services = ref([])

// Fetch data
const [{ data: teamData }, { data: portfolioData }, { data: servicesData }] = await Promise.all([
  useFetch('/api/team/', { lazy: true, server: false }),
  useFetch('/api/portfolio/', { lazy: true, server: false }),
  useFetch('/api/services/', { lazy: true, server: false })
])

watch(teamData, (val) => { if (val) team.value = val }, { immediate: true })
watch(portfolioData, (val) => { if (val) portfolio.value = val }, { immediate: true })
watch(servicesData, (val) => { if (val) services.value = val }, { immediate: true })

const topServices = computed(() => services.value.slice(0, 3))

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

.hero__bg-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0.4;
  filter: saturate(1.2) brightness(0.8);
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
