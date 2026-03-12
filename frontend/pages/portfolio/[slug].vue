<template>
  <div class="section">
    <div class="container" v-if="project">
      <!-- Back link -->
      <NuxtLink to="/portfolio" class="project-back">
        ← Назад к портфолио
      </NuxtLink>

      <!-- Project Hero -->
      <div class="project-hero">
        <div class="project-hero__image">
          <div class="project-hero__placeholder">
            {{ project.title.charAt(0) }}
          </div>
        </div>

        <div class="project-hero__info">
          <div class="project-hero__tags" v-if="tagsList.length">
            <span v-for="tag in tagsList" :key="tag" class="project-hero__tag">{{ tag }}</span>
          </div>
          <h1 class="project-hero__title">{{ project.title }}</h1>
          <p class="project-hero__short">{{ project.short_description }}</p>
        </div>
      </div>

      <!-- Full description -->
      <div class="project-description card">
        <h2 class="project-description__title">О проекте</h2>
        <p class="project-description__text">{{ project.full_description }}</p>
      </div>

      <!-- CTA -->
      <div class="project-cta text-center">
        <p>Хотите похожий проект?</p>
        <button class="btn btn-primary" @click="openChat">
          💬 Обсудить задачу
        </button>
      </div>
    </div>

    <div class="container text-center" v-else>
      <p style="color: var(--c-text-muted); padding: var(--space-4xl) 0">
        Проект не найден
      </p>
      <NuxtLink to="/portfolio" class="btn btn-outline">← К портфолио</NuxtLink>
    </div>
  </div>
</template>

<script setup>
const route = useRoute()
const slug = route.params.slug

const { data: project } = await useFetch(`/api/portfolio/${slug}`)

if (project.value) {
  useHead({
    title: `${project.value.title} — Портфолио Khudyakov Inc.`,
    meta: [
      { name: 'description', content: project.value.short_description },
    ],
  })
}

const tagsList = computed(() =>
  project.value?.tags
    ? project.value.tags.split(',').map((t) => t.trim()).filter(Boolean)
    : []
)

const openChat = () => {
  const toggle = document.getElementById('chat-toggle')
  if (toggle) toggle.click()
}
</script>

<style scoped>
.project-back {
  display: inline-block;
  color: var(--c-text-muted);
  font-size: 0.9rem;
  margin-bottom: var(--space-2xl);
  transition: color var(--duration-fast);
}

.project-back:hover {
  color: var(--c-accent-light);
}

/* ── Hero ─────────────────────────────── */
.project-hero {
  margin-bottom: var(--space-3xl);
}

.project-hero__image {
  width: 100%;
  height: 360px;
  border-radius: var(--radius-xl);
  overflow: hidden;
  margin-bottom: var(--space-2xl);
  border: 1px solid var(--c-border);
}

.project-hero__placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--c-gradient-2);
  font-size: 5rem;
  font-weight: 900;
  color: #fff;
}

.project-hero__tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-sm);
  margin-bottom: var(--space-md);
}

.project-hero__tag {
  padding: 0.3rem 0.8rem;
  background: var(--c-bg-glass);
  border: 1px solid var(--c-border);
  border-radius: var(--radius-full);
  font-size: 0.8rem;
  color: var(--c-accent-light);
}

.project-hero__title {
  font-size: 2.5rem;
  font-weight: 800;
  margin-bottom: var(--space-md);
}

.project-hero__short {
  color: var(--c-text-secondary);
  font-size: 1.1rem;
  line-height: 1.7;
}

/* ── Description ──────────────────────── */
.project-description {
  padding: var(--space-3xl);
  margin-bottom: var(--space-3xl);
}

.project-description__title {
  font-size: 1.3rem;
  font-weight: 700;
  margin-bottom: var(--space-lg);
}

.project-description__text {
  color: var(--c-text-secondary);
  font-size: 1rem;
  line-height: 1.8;
  white-space: pre-line;
}

/* ── CTA ──────────────────────────────── */
.project-cta {
  padding: var(--space-2xl);
}

.project-cta p {
  color: var(--c-text-secondary);
  margin-bottom: var(--space-lg);
  font-size: 1.1rem;
}

@media (max-width: 768px) {
  .project-hero__title {
    font-size: 1.8rem;
  }

  .project-hero__image {
    height: 220px;
  }
}
</style>
