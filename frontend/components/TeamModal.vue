<template>
  <Teleport to="body">
    <div class="modal-overlay" @click.self="$emit('close')">
      <div class="modal-content">
        <button class="modal-close" @click="$emit('close')">&times;</button>

        <div class="modal-header">
          <div class="modal-avatar">
            <div class="modal-avatar__placeholder">
              {{ member.name.charAt(0) }}
            </div>
          </div>
          <div>
            <h2 class="modal-name">{{ member.name }}</h2>
            <p class="modal-position">{{ member.position }}</p>
          </div>
        </div>

        <div class="modal-section">
          <h4 class="modal-label">Технологический стек</h4>
          <div class="modal-tags">
            <span v-for="tech in stackList" :key="tech" class="modal-tag">{{ tech }}</span>
          </div>
        </div>

        <div class="modal-section">
          <h4 class="modal-label">Опыт и компетенции</h4>
          <p class="modal-description">{{ member.description }}</p>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
const props = defineProps({
  member: {
    type: Object,
    required: true,
  },
})

defineEmits(['close'])

const stackList = computed(() =>
  props.member.stack.split(',').map((s) => s.trim()).filter(Boolean)
)

// Close on Escape key
onMounted(() => {
  const handler = (e) => {
    if (e.key === 'Escape') {
      // emit close through the parent
      document.querySelector('.modal-overlay')?.click()
    }
  }
  document.addEventListener('keydown', handler)
  onUnmounted(() => document.removeEventListener('keydown', handler))
})
</script>

<style scoped>
.modal-close {
  position: absolute;
  top: var(--space-lg);
  right: var(--space-lg);
  background: none;
  border: none;
  color: var(--c-text-secondary);
  font-size: 2rem;
  cursor: pointer;
  line-height: 1;
  transition: color var(--duration-fast);
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
}

.modal-close:hover {
  color: var(--c-text-primary);
  background: var(--c-bg-glass);
}

.modal-header {
  display: flex;
  align-items: center;
  gap: var(--space-lg);
  margin-bottom: var(--space-2xl);
}

.modal-avatar {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
  border: 2px solid var(--c-accent);
}

.modal-avatar__placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--c-gradient-1);
  color: #fff;
  font-size: 1.6rem;
  font-weight: 700;
}

.modal-name {
  font-size: 1.4rem;
  font-weight: 700;
}

.modal-position {
  color: var(--c-accent-light);
  font-size: 0.95rem;
  margin-top: var(--space-xs);
}

.modal-section {
  margin-bottom: var(--space-xl);
}

.modal-label {
  color: var(--c-text-muted);
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: var(--space-sm);
}

.modal-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-sm);
}

.modal-tag {
  padding: 0.3rem 0.8rem;
  background: var(--c-bg-glass);
  border: 1px solid var(--c-border);
  border-radius: var(--radius-full);
  font-size: 0.85rem;
  color: var(--c-accent-light);
}

.modal-description {
  color: var(--c-text-secondary);
  font-size: 0.95rem;
  line-height: 1.7;
}
</style>
