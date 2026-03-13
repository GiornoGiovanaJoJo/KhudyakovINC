<template>
  <div class="project-page" v-if="project">
    <!-- Hero Section -->
    <div class="project-hero" :style="{ backgroundImage: project.image_url ? `url(${project.image_url})` : '' }">
      <div v-if="!project.image_url" class="project-hero__placeholder text-gradient">
        {{ project.title.charAt(0) }}
      </div>
      <div class="project-hero__overlay"></div>
      <div class="container project-hero__content">
        <NuxtLink to="/portfolio" class="back-link">
          <span>←</span> Назад в портфолио
        </NuxtLink>
        <h1 class="project-title">{{ project.title }}</h1>
        <div class="project-tags">
          <span v-for="tag in tagsList" :key="tag" class="tag">
            {{ tag }}
          </span>
        </div>
      </div>
    </div>

    <!-- Content Section -->
    <div class="container project-main">
      <div class="project-grid">
        <!-- Description -->
        <div class="project-info">
          <section class="project-section card">
            <h2 class="section-title">О проекте</h2>
            <div class="project-description-text" v-html="project.full_description"></div>
          </section>

          <!-- Interactive Figma Embed -->
          <section class="project-section" v-if="project.figma_url">
            <h2 class="section-title">Интерактивный прототип</h2>
            <div class="figma-container glass">
              <iframe 
                style="border: 1px solid rgba(0, 0, 0, 0.1); width: 100%; height: 600px;" 
                :src="`https://www.figma.com/embed?embed_host=share&url=${project.figma_url}`" 
                allowfullscreen
              ></iframe>
            </div>
          </section>

          <!-- Gallery -->
          <section class="project-section" v-if="project.gallery?.length">
            <h2 class="section-title">Галерея экранов</h2>
            <div class="project-gallery">
              <img 
                v-for="(img, idx) in project.gallery" 
                :key="idx" 
                :src="img" 
                class="gallery-image" 
                alt="Screen preview"
                @error="project.gallery.splice(idx, 1)"
              >
            </div>
          </section>
        </div>

        <!-- Sidebar Actions -->
        <aside class="project-sidebar">
          <div class="sticky-card glass">
            <h3 class="card-title">Хотите такой же проект?</h3>
            <p class="card-text">Обсудите вашу идею с нами прямо сейчас.</p>
            <button @click="openChat" class="btn btn-primary w-full">Обсудить проект</button>
            
            <div v-if="project.external_url" class="external-links">
              <hr class="card-hr">
              <button @click="isBrowserOpen = true" class="btn btn-outline w-full">
                Посмотреть живой сайт ↗
              </button>
            </div>
          </div>
        </aside>
      </div>
    </div>

    <!-- Internal Browser Modal -->
    <Transition name="fade">
      <div v-if="isBrowserOpen" class="browser-modal">
        <div class="browser-modal__header glass">
          <div class="browser-modal__address">
            <span class="lock-icon">🔒</span>
            <span class="url-text">{{ project.external_url }}</span>
          </div>
          <button @click="isBrowserOpen = false" class="browser-modal__close">✕</button>
        </div>
        <div class="browser-modal__content">
          <iframe :src="project.external_url" frameborder="0" class="browser-iframe"></iframe>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
const route = useRoute()
const slug = route.params.slug
const isBrowserOpen = ref(false)

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
.project-page {
  background: var(--c-bg-primary);
  padding-bottom: var(--space-4xl);
}

.project-hero {
  height: 60vh;
  background-size: cover;
  background-position: center;
  position: relative;
  display: flex;
  align-items: flex-end;
  padding-bottom: var(--space-3xl);
}

.project-hero__placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 8rem;
  font-weight: 900;
  background: var(--c-bg-secondary);
}

.project-hero__overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to bottom, rgba(0,0,0,0.3), var(--c-bg-primary));
}

.project-hero__content {
  position: relative;
  z-index: 2;
}

.back-link {
  color: var(--c-text-secondary);
  text-decoration: none;
  font-size: 0.9rem;
  margin-bottom: var(--space-md);
  display: inline-block;
  transition: color var(--duration-fast);
}

.back-link:hover {
  color: var(--c-accent-light);
}

.project-title {
  font-size: clamp(2rem, 5vw, 4rem);
  font-weight: 900;
  line-height: 1.1;
  margin-bottom: var(--space-md);
  letter-spacing: -0.04em;
}

.project-tags {
  display: flex;
  gap: var(--space-sm);
  flex-wrap: wrap;
}

.tag {
  background: rgba(255,255,255,0.08);
  padding: 6px 16px;
  border-radius: var(--radius-full);
  font-size: 0.8rem;
  font-weight: 600;
  backdrop-filter: blur(10px);
  border: 1px solid var(--c-border);
  color: var(--c-accent-light);
}

.project-main {
  margin-top: -60px;
  position: relative;
  z-index: 10;
}

.project-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: var(--space-3xl);
}

.project-section {
  margin-bottom: var(--space-3xl);
  padding: var(--space-2xl);
}

.section-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: var(--space-xl);
  color: var(--c-text-primary);
}

.project-description-text {
  font-size: 1.05rem;
  line-height: 1.8;
  color: var(--c-text-secondary);
  white-space: pre-line;
}

.figma-container {
  border-radius: var(--radius-2xl);
  overflow: hidden;
  border: 1px solid var(--c-border);
}

.project-gallery {
  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
}

.gallery-image {
  width: 100%;
  border-radius: var(--radius-xl);
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
  border: 1px solid var(--c-border);
}

.sticky-card {
  position: sticky;
  top: 100px;
  padding: var(--space-2xl);
  border-radius: var(--radius-xl);
  text-align: center;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: var(--space-sm);
}

.card-text {
  color: var(--c-text-secondary);
  font-size: 0.95rem;
  margin-bottom: var(--space-xl);
}

.card-hr {
  border: 0;
  border-top: 1px solid var(--c-border);
  margin: var(--space-xl) 0;
}

.w-full { width: 100%; }


/* ── Browser Modal ────────────────────── */
.browser-modal {
  position: fixed;
  inset: 0;
  z-index: 2000;
  background: var(--c-bg-primary);
  display: flex;
  flex-direction: column;
}

.browser-modal__header {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-xl);
  border-bottom: 1px solid var(--c-border);
}

.browser-modal__address {
  background: rgba(255, 255, 255, 0.05);
  padding: 0.5rem 1.5rem;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: var(--c-text-muted);
  border: 1px solid var(--c-border);
  max-width: 60%;
}

.url-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.browser-modal__close {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: var(--c-text-primary);
  cursor: pointer;
  padding: 0.5rem;
}

.browser-modal__content {
  flex: 1;
  background: #fff;
}

.browser-iframe {
  width: 100%;
  height: 100%;
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

@media (max-width: 900px) {
  .project-grid {
    grid-template-columns: 1fr;
  }
}
</style>
