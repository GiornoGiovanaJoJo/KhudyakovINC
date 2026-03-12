<template>
  <NuxtLink :to="`/portfolio/${project.slug}`" class="portfolio-card card">
    <div class="portfolio-card__image">
      <div class="portfolio-card__image-placeholder">
        <span>{{ project.title.charAt(0) }}</span>
      </div>
    </div>
    <div class="portfolio-card__body">
      <h3 class="portfolio-card__title">{{ project.title }}</h3>
      <p class="portfolio-card__desc">{{ project.short_description }}</p>
      <div class="portfolio-card__tags" v-if="tagsList.length">
        <span v-for="tag in tagsList" :key="tag" class="portfolio-card__tag">{{ tag }}</span>
      </div>
    </div>
    <div class="portfolio-card__arrow">→</div>
  </NuxtLink>
</template>

<script setup>
const props = defineProps({
  project: {
    type: Object,
    required: true,
  },
})

const tagsList = computed(() =>
  props.project.tags ? props.project.tags.split(',').map((t) => t.trim()).filter(Boolean) : []
)
</script>

<style scoped>
.portfolio-card {
  display: flex;
  flex-direction: column;
  text-decoration: none;
  color: inherit;
  overflow: hidden;
  padding: 0;
}

.portfolio-card__image {
  width: 100%;
  height: 200px;
  overflow: hidden;
  background: var(--c-bg-secondary);
}

.portfolio-card__image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--c-gradient-2);
  opacity: 0.7;
  transition: opacity var(--duration-normal) var(--ease-out);
}

.portfolio-card:hover .portfolio-card__image-placeholder {
  opacity: 1;
}

.portfolio-card__image-placeholder span {
  font-size: 3rem;
  font-weight: 800;
  color: #fff;
}

.portfolio-card__body {
  padding: var(--space-xl);
  flex: 1;
}

.portfolio-card__title {
  font-size: 1.15rem;
  font-weight: 700;
  margin-bottom: var(--space-sm);
}

.portfolio-card__desc {
  color: var(--c-text-secondary);
  font-size: 0.9rem;
  line-height: 1.5;
  margin-bottom: var(--space-md);
}

.portfolio-card__tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-xs);
}

.portfolio-card__tag {
  padding: 0.2rem 0.5rem;
  background: var(--c-bg-glass);
  border: 1px solid var(--c-border);
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  color: var(--c-text-muted);
}

.portfolio-card__arrow {
  padding: var(--space-md) var(--space-xl);
  border-top: 1px solid var(--c-border);
  text-align: right;
  color: var(--c-accent-light);
  font-size: 1.2rem;
  opacity: 0;
  transform: translateX(-8px);
  transition: all var(--duration-normal) var(--ease-out);
}

.portfolio-card:hover .portfolio-card__arrow {
  opacity: 1;
  transform: translateX(0);
}
</style>
