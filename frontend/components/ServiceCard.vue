<template>
  <div class="service-card card card-glow" ref="cardEl">
    <div class="service-card__icon">{{ service.icon }}</div>
    <h3 class="service-card__title">{{ service.title }}</h3>
    <p class="service-card__desc">{{ service.description }}</p>
  </div>
</template>

<script setup>
import { useTilt } from '~/composables/useAnimations'

const props = defineProps({
  service: {
    type: Object,
    required: true,
  },
})

const cardEl = ref(null)
useTilt(cardEl, 6)
</script>

<style scoped>
.service-card {
  text-align: center;
  padding: var(--space-2xl) var(--space-xl);
  will-change: transform;
}

.service-card__icon {
  font-size: 2.5rem;
  margin-bottom: var(--space-lg);
  display: inline-block;
  animation: float 4s ease-in-out infinite;
}

.service-card__title {
  font-size: 1.15rem;
  font-weight: 700;
  margin-bottom: var(--space-sm);
}

.service-card__desc {
  color: var(--c-text-secondary);
  font-size: 0.9rem;
  line-height: 1.6;
}
</style>
