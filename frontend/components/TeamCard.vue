<template>
  <div class="team-card card" @click="$emit('select', member)" tabindex="0">
    <div class="team-card__avatar">
      <div class="team-card__avatar-placeholder">
        {{ member.name.charAt(0) }}
      </div>
    </div>
    <h3 class="team-card__name">{{ member.name }}</h3>
    <p class="team-card__position">{{ member.position }}</p>
    <div class="team-card__stack">
      <span v-for="tech in stackList" :key="tech" class="team-card__tag">
        {{ tech }}
      </span>
    </div>
    <div class="team-card__hint">Нажмите для подробностей →</div>
  </div>
</template>

<script setup>
const props = defineProps({
  member: {
    type: Object,
    required: true,
  },
})

defineEmits(['select'])

const stackList = computed(() =>
  props.member.stack.split(',').map((s) => s.trim()).filter(Boolean)
)
</script>

<style scoped>
.team-card {
  cursor: pointer;
  text-align: center;
  padding: var(--space-2xl) var(--space-xl);
}

.team-card:hover {
  border-color: var(--c-accent);
}

.team-card__avatar {
  width: 100px;
  height: 100px;
  margin: 0 auto var(--space-lg);
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid var(--c-border);
  transition: border-color var(--duration-normal) var(--ease-out);
}

.team-card:hover .team-card__avatar {
  border-color: var(--c-accent);
  box-shadow: var(--shadow-glow);
}

.team-card__avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--c-gradient-1);
  color: #fff;
  font-size: 2.2rem;
  font-weight: 700;
}

.team-card__name {
  font-size: 1.2rem;
  font-weight: 700;
  margin-bottom: var(--space-xs);
}

.team-card__position {
  color: var(--c-accent-light);
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: var(--space-md);
}

.team-card__stack {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: var(--space-xs);
  margin-bottom: var(--space-md);
}

.team-card__tag {
  padding: 0.2rem 0.6rem;
  background: var(--c-bg-glass);
  border: 1px solid var(--c-border);
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  color: var(--c-text-secondary);
}

.team-card__hint {
  color: var(--c-text-muted);
  font-size: 0.8rem;
  opacity: 0;
  transform: translateY(4px);
  transition: all var(--duration-normal) var(--ease-out);
}

.team-card:hover .team-card__hint {
  opacity: 1;
  transform: translateY(0);
}
</style>
