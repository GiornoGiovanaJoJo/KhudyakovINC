<template>
  <div>
    <!-- Hero Section -->
    <section class="hero">
      <div class="hero__bg">
        <InteractiveHero />
      </div>
      <div class="container hero__content">
        <div class="hero__badge reveal">🚀 Команда профессионалов</div>
        <h1 class="hero__title">
          Превращаем идеи <br />
          в <span class="text-gradient typewriter-word">{{ typedText }}<span class="typewriter-cursor"></span></span>
        </h1>
        <p class="hero__subtitle">
          Веб-разработка, дизайн и IT-консалтинг.
          Полный цикл: от идеи до запуска.
        </p>
        <div class="hero__actions">
          <NuxtLink to="/portfolio" class="btn btn-primary" ref="btnPortfolio">Наши работы</NuxtLink>
          <NuxtLink to="/services" class="btn btn-outline" ref="btnServices">Услуги</NuxtLink>
        </div>

        <div class="hero__stats">
          <div class="hero__stat" ref="stat1">
            <div class="hero__stat-value">{{ countProjects }}</div>
            <div class="hero__stat-label">Проектов</div>
          </div>
          <div class="hero__stat" ref="stat2">
            <div class="hero__stat-value">{{ countYears }}</div>
            <div class="hero__stat-label">Лет опыта</div>
          </div>
          <div class="hero__stat" ref="stat3">
            <div class="hero__stat-value">{{ countClients }}</div>
            <div class="hero__stat-label">Довольных клиентов</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Project Quiz (Kwiz) -->
    <section class="section quiz-bg">
      <div class="container">
        <div class="quiz-card glass reveal">
          <div v-if="!quizCompleted">
            <div class="quiz-progress">
              <div class="quiz-progress__bar" :style="{ width: ((quizStep + 1) / quizSteps.length) * 100 + '%' }"></div>
            </div>
            <h2 class="quiz-title">{{ quizSteps[quizStep].question }}</h2>
            <div class="quiz-options">
              <button
                v-for="option in quizSteps[quizStep].options"
                :key="option"
                class="quiz-option"
                @click="selectOption(option)"
              >
                {{ option }}
              </button>
            </div>
          </div>
          <div v-else class="text-center">
            <h2 class="quiz-title">Отлично! Мы почти готовы</h2>
            <p class="mb-lg">Я подготовил предварительный план на основе ваших ответов. Давайте обсудим детали в чате.</p>
            <button class="btn btn-primary" @click="startChatWithQuiz">💬 Обсудить в чате</button>
          </div>
        </div>
      </div>
    </section>

    <hr class="section-divider" />

    <!-- Services Overview -->
    <section class="section">
      <div class="container">
        <h2 class="section__title reveal">Что мы умеем</h2>
        <p class="section__subtitle reveal">
          Мы предлагаем комплексные решения для запуска и развития вашего бизнеса в цифровой среде.
        </p>
        <div class="grid-3 reveal-cascade">
          <ServiceCard
            v-for="service in topServices"
            :key="service.id"
            :service="service"
            class="reveal"
          />
        </div>
        <div class="text-center mt-xl reveal">
          <NuxtLink to="/services" class="btn btn-outline">Посмотреть все услуги</NuxtLink>
        </div>
      </div>
    </section>

    <hr class="section-divider" />

    <!-- Portfolio Highlights -->
    <section class="section" style="background: var(--c-bg-secondary)">
      <div class="container">
        <h2 class="section__title reveal">Наши работы</h2>
        <p class="section__subtitle reveal">
          Проекты, которыми мы гордимся. Каждый из них — это уникальное решение сложной задачи.
        </p>
        <div class="grid-3 reveal-cascade" v-if="portfolio.length">
          <PortfolioCard
            v-for="project in portfolio.slice(0, 3)"
            :key="project.id"
            :project="project"
            class="reveal"
          />
        </div>
        <div class="text-center mt-xl reveal">
          <NuxtLink to="/portfolio" class="btn btn-outline">Весь портфель</NuxtLink>
        </div>
      </div>
    </section>

    <hr class="section-divider" />

    <!-- How We Work -->
    <section class="section">
      <div class="container">
        <h2 class="section__title reveal">Как мы работаем</h2>
        <p class="section__subtitle reveal">
          Наш процесс прозрачен и эффективен. Мы сопровождаем вас на каждом этапе создания продукта.
        </p>
        <div class="process-grid reveal-cascade">
          <div class="process-step reveal">
            <div class="process-step__icon float-subtle">
              <img src="/images/steps/analytics.png" alt="Analytics">
            </div>
            <h3 class="process-step__title">Аналитика</h3>
            <p class="process-step__desc">Погружаемся в ваш бизнес, определяем цели и требования.</p>
          </div>
          <div class="process-step reveal">
            <div class="process-step__icon float-subtle" style="animation-delay: 0.5s">
              <img src="/images/steps/design.png" alt="Design">
            </div>
            <h3 class="process-step__title">Дизайн</h3>
            <p class="process-step__desc">Создаем удобные и современные интерфейсы (UI/UX).</p>
          </div>
          <div class="process-step reveal">
            <div class="process-step__icon float-subtle" style="animation-delay: 1s">
              <img src="/images/steps/dev.png" alt="Development">
            </div>
            <h3 class="process-step__title">Разработка</h3>
            <p class="process-step__desc">Пишем чистый код, используя передовой стек технологий.</p>
          </div>
          <div class="process-step reveal">
            <div class="process-step__icon float-subtle" style="animation-delay: 1.5s">
              <img src="/images/steps/launch.png" alt="Launch">
            </div>
            <h3 class="process-step__title">Запуск</h3>
            <p class="process-step__desc">Тестируем и выводим проект на рынок, обеспечивая поддержку.</p>
          </div>
        </div>
      </div>
    </section>

    <hr class="section-divider" />

    <!-- Team Section -->
    <section class="section" id="team" style="background: var(--c-bg-secondary)">
      <div class="container">
        <h2 class="section__title reveal">Наша команда</h2>
        <p class="section__subtitle reveal">
          Профессионалы, которые создают ваш продукт
        </p>

        <div class="grid-3 reveal-cascade" v-if="team.length">
          <TeamCard
            v-for="member in team"
            :key="member.id"
            :member="member"
            @select="selectedMember = member"
            class="reveal"
          />
        </div>

        <p v-else class="text-center" style="color: var(--c-text-muted)">
          Загрузка команды...
        </p>
      </div>
    </section>

    <hr class="section-divider" />

    <!-- FAQ Section -->
    <section class="section">
      <div class="container">
        <h2 class="section__title reveal">Часто задаваемые вопросы</h2>
        <div class="faq-list">
          <div
            v-for="faq in faqItems"
            :key="faq.question"
            class="faq-item reveal"
            :class="{ 'faq-item--open': faq.open }"
            @click="toggleFaq(faq)"
          >
            <div class="faq-item__header">
              <h3 class="faq-item__question">{{ faq.question }}</h3>
              <span class="faq-item__arrow">▼</span>
            </div>
            <div class="faq-item__answer">
              <p>{{ faq.answer }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <hr class="section-divider" />

    <!-- Tech Stack — Interactive Grid -->
    <section class="section" style="background: var(--c-bg-secondary)">
      <div class="container">
        <h2 class="section__title reveal">Наш технологический стек</h2>
        <p class="section__subtitle reveal">Используем проверенные технологии для надёжных решений</p>
        <div class="tech-orbit-grid reveal-cascade">
          <div
            v-for="(tech, i) in techStack"
            :key="tech.name"
            class="tech-orbit-card glass reveal"
            :style="{ animationDelay: (i * 0.4) + 's' }"
          >
            <div class="tech-orbit-card__glow"></div>
            <div class="tech-orbit-card__icon">
              <img :src="tech.icon" :alt="tech.name">
            </div>
            <div class="tech-orbit-card__name">{{ tech.name }}</div>
            <div class="tech-orbit-card__desc">{{ tech.desc }}</div>
          </div>
        </div>
      </div>
    </section>

    <hr class="section-divider" />

    <!-- Testimonials -->
    <section class="section testimonials-bg">
      <div class="container">
        <h2 class="section__title reveal">Что говорят клиенты</h2>
        <div class="testimonials-slider">
          <div v-for="t in testimonials" :key="t.name" class="testimonial-card glass reveal">
            <p class="testimonial-text">"{{ t.text }}"</p>
            <div class="testimonial-author">
              <div class="testimonial-avatar">{{ t.name[0] }}</div>
              <div>
                <div class="testimonial-name">{{ t.name }}</div>
                <div class="testimonial-role">{{ t.role }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <TeamModal
      v-if="selectedMember"
      :member="selectedMember"
      @close="selectedMember = null"
    />

    <!-- CTA Section -->
    <section class="cta section">
      <div class="container text-center">
        <h2 class="section__title reveal">Готовы обсудить проект?</h2>
        <p class="section__subtitle mb-xl reveal">
          Расскажите о вашей задаче в чате — наш ИИ-консультант ответит мгновенно
          и поможет подготовить коммерческое предложение.
        </p>
        <button class="btn btn-primary btn-pulse reveal" @click="openChat">💬 Начать диалог</button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { useScrollReveal, useCountUp, useTypewriter } from '~/composables/useAnimations'

useHead({
  title: 'Khudyakov Inc. — Веб-разработка, дизайн и IT-решения',
})

// ─── Scroll Reveal ────────────────────────────────────
useScrollReveal()

// ─── Typewriter Effect ────────────────────────────────
const { displayText: typedText } = useTypewriter(
  ['цифровые продукты', 'веб-приложения', 'мобильные решения', 'CRM-системы', 'стартапы'],
  90,
  40,
  2500
)

// ─── Animated Counters ────────────────────────────────
const stat1 = ref(null)
const stat2 = ref(null)
const stat3 = ref(null)
const countProjects = useCountUp(stat1, 50, 2000, '+')
const countYears = useCountUp(stat2, 5, 1500, '+')
const countClients = useCountUp(stat3, 30, 1800, '+')

// ─── State ────────────────────────────────────────────
const selectedMember = ref(null)
const team = ref([])
const portfolio = ref([])
const services = ref([])

// ─── FAQ Accordion ────────────────────────────────────
const faqItems = ref([
  {
    question: 'Сколько времени занимает разработка?',
    answer: 'Сроки зависят от сложности проекта. Корпоративный сайт — от 2 недель, сложный сервис или CRM — от 1.5 месяцев.',
    open: false,
  },
  {
    question: 'Какие технологии вы используете?',
    answer: 'Мы работаем с современным стеком: Vue.js/Nuxt.js, React, Node.js, Python (FastAPI/Django), PostgreSQL и Docker.',
    open: false,
  },
  {
    question: 'Оказываете ли вы поддержку после запуска?',
    answer: 'Да, мы предлагаем гарантийное обслуживание в течение года и услуги по развитию вашего продукта.',
    open: false,
  },
])

const toggleFaq = (targetItem) => {
  faqItems.value.forEach((item) => {
    if (item === targetItem) {
      item.open = !item.open
    } else {
      item.open = false
    }
  })
}

// Quiz Logic
const quizStep = ref(0)
const quizCompleted = ref(false)
const quizAnswers = ref([])
const quizSteps = [
  {
    question: "Тип вашего проекта?",
    options: ["Веб-сайт", "Интернет-магазин", "Сложный сервис", "Консультация"]
  },
  {
    question: "Нужен ли дизайн?",
    options: ["Да, с нуля", "Есть свой макет", "Нужен редизайн", "Не требуется"]
  },
  {
    question: "Примерные сроки?",
    options: ["Как можно быстрее", "1-2 месяца", "Более 3 месяцев", "Пока обсуждаемо"]
  }
]

const selectOption = (option) => {
  quizAnswers.value.push(option)
  if (quizStep.value < quizSteps.length - 1) {
    quizStep.value++
  } else {
    quizCompleted.value = true
    const context = {
      type: quizAnswers.value[0],
      design: quizAnswers.value[1],
      timeline: quizAnswers.value[2]
    }
    localStorage.setItem('quiz_context', JSON.stringify(context))
  }
}

const startChatWithQuiz = () => {
  openChat()
}

// Content Data
const techStack = [
  { name: "Vue / Nuxt", icon: "/images/icons/vue.png", desc: "Реактивные интерфейсы и SSR" },
  { name: "Node.js", icon: "/images/icons/node.png", desc: "Высоконагруженные API" },
  { name: "Python / FastAPI", icon: "/images/icons/python.png", desc: "ML, автоматизация, бэкенд" },
  { name: "PostgreSQL", icon: "/images/icons/postgres.png", desc: "Надёжное хранение данных" },
  { name: "Docker", icon: "/images/icons/docker.png", desc: "Контейнеризация и деплой" },
  { name: "Figma", icon: "/images/icons/figma.png", desc: "UI/UX дизайн и прототипы" }
]

const testimonials = [
  { name: "Александр В.", role: "CEO TechStart", text: "Профессиональный подход и высокая скорость разработки. Реализовали сложную CRM за рекордные сроки." },
  { name: "Мария К.", role: "Marketing Director", text: "Студия помогла нам полностью переосмыслить дизайн. Конверсия на сайте выросла в 2 раза!" },
  { name: "Иван П.", role: "Founder RetailPro", text: "Надежные ребята. Поддержка 24/7 и качественный код. Работаем на постоянной основе." }
]

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

// ─── Magnetic Buttons ─────────────────────────────────
const btnPortfolio = ref(null)
const btnServices = ref(null)

onMounted(() => {
  // Magnetic effect for hero buttons
  const magneticSetup = (el) => {
    if (!el?.$el) return
    const node = el.$el
    node.addEventListener('mousemove', (e) => {
      const rect = node.getBoundingClientRect()
      const x = e.clientX - rect.left - rect.width / 2
      const y = e.clientY - rect.top - rect.height / 2
      node.style.transform = `translate(${x * 0.25}px, ${y * 0.25}px)`
      node.style.transition = 'transform 0.15s ease'
    })
    node.addEventListener('mouseleave', () => {
      node.style.transform = 'translate(0, 0)'
      node.style.transition = 'transform 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)'
    })
  }

  magneticSetup(btnPortfolio.value)
  magneticSetup(btnServices.value)
})
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
  animation: pulseOrb 6s ease-in-out infinite;
}

@keyframes pulseOrb {
  0%, 100% { opacity: 0.3; transform: translateX(-50%) scale(1); }
  50% { opacity: 0.55; transform: translateX(-50%) scale(1.1); }
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

.typewriter-word {
  display: inline;
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
  position: relative;
  overflow: hidden;
}

.cta::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle at center, var(--c-accent-glow) 0%, transparent 50%);
  opacity: 0.08;
  animation: rotateBg 20s linear infinite;
}

@keyframes rotateBg {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
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

/* ── Quiz ──────────────────────────────────── */
.quiz-bg {
  background: radial-gradient(circle at 10% 20%, rgba(99, 102, 241, 0.05) 0%, transparent 50%);
}

.quiz-card {
  max-width: 700px;
  margin: 0 auto;
  padding: var(--space-2xl);
  border-radius: var(--radius-lg);
  min-height: 350px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.quiz-progress {
  height: 4px;
  background: var(--c-bg-card);
  border-radius: var(--radius-full);
  margin-bottom: var(--space-xl);
  overflow: hidden;
}

.quiz-progress__bar {
  height: 100%;
  background: var(--c-accent);
  transition: width 0.4s var(--ease-out);
}

.quiz-title {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: var(--space-xl);
  text-align: center;
}

.quiz-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-md);
}

.quiz-option {
  padding: 1rem;
  background: var(--c-bg-card);
  border: 1px solid var(--c-border);
  border-radius: var(--radius-md);
  color: var(--c-text-secondary);
  font-family: var(--font-main);
  font-size: 1rem;
  cursor: pointer;
  transition: all var(--duration-fast);
  position: relative;
  overflow: hidden;
}

.quiz-option::before {
  content: '';
  position: absolute;
  inset: 0;
  background: var(--c-gradient-1);
  opacity: 0;
  transition: opacity 0.3s;
}

.quiz-option:hover {
  background: var(--c-bg-glass);
  border-color: var(--c-accent);
  color: var(--c-text-primary);
  transform: translateY(-2px);
}

/* ── Tech Stack — Orbit Grid ────────────── */
.tech-orbit-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-xl);
}

.tech-orbit-card {
  position: relative;
  text-align: center;
  padding: var(--space-2xl) var(--space-xl);
  border-radius: var(--radius-lg);
  transition: all 0.4s var(--ease-out);
  animation: techBreathe 5s ease-in-out infinite;
  will-change: transform;
  overflow: hidden;
}

.tech-orbit-card:nth-child(even) {
  animation-direction: reverse;
}

@keyframes techBreathe {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

.tech-orbit-card__glow {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 50% 50%, var(--c-accent-glow) 0%, transparent 70%);
  opacity: 0;
  transition: opacity 0.5s ease;
  pointer-events: none;
}

.tech-orbit-card:hover .tech-orbit-card__glow {
  opacity: 0.3;
}

.tech-orbit-card:hover {
  transform: translateY(-8px) scale(1.03);
  border-color: var(--c-accent);
  box-shadow: 0 8px 40px var(--c-accent-glow);
}

.tech-orbit-card__icon {
  width: 56px;
  height: 56px;
  margin: 0 auto var(--space-md);
  transition: transform 0.5s var(--ease-spring);
}

.tech-orbit-card__icon img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.tech-orbit-card:hover .tech-orbit-card__icon {
  transform: scale(1.2) rotate(8deg);
}

.tech-orbit-card__name {
  font-size: 1.05rem;
  font-weight: 700;
  margin-bottom: var(--space-xs);
  color: var(--c-text-primary);
}

.tech-orbit-card__desc {
  font-size: 0.85rem;
  color: var(--c-text-muted);
  line-height: 1.5;
  transition: color 0.3s;
}

.tech-orbit-card:hover .tech-orbit-card__desc {
  color: var(--c-text-secondary);
}

@media (max-width: 768px) {
  .tech-orbit-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-md);
  }
}

/* ── Testimonials ──────────────────────────── */
.testimonials-bg {
  background: radial-gradient(circle at 90% 80%, rgba(99, 102, 241, 0.05) 0%, transparent 50%);
}

.testimonials-slider {
  display: flex;
  gap: var(--space-xl);
  overflow-x: auto;
  padding: var(--space-xl) var(--space-sm);
  scrollbar-width: none;
  scroll-snap-type: x mandatory;
}

.testimonials-slider::-webkit-scrollbar { display: none; }

.testimonial-card {
  min-width: 320px;
  padding: var(--space-xl);
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  scroll-snap-align: start;
  transition: transform 0.3s var(--ease-out), box-shadow 0.3s;
}

.testimonial-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-card);
}

.testimonial-text {
  font-style: italic;
  font-size: 1rem;
  line-height: 1.6;
  margin-bottom: var(--space-xl);
  flex-grow: 1;
}

.testimonial-author {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.testimonial-avatar {
  width: 45px;
  height: 45px;
  background: var(--c-gradient-1);
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  color: white;
}

.testimonial-name {
  font-weight: 700;
  font-size: 0.95rem;
}

.testimonial-role {
  font-size: 0.8rem;
  color: var(--c-text-muted);
}

.mt-xl {
  margin-top: var(--space-xl);
}
</style>
