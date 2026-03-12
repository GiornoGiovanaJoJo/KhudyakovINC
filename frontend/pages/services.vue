<template>
  <div class="section">
    <div class="container">
      <h1 class="section__title">Наши услуги</h1>
      <p class="section__subtitle">
        Полный спектр IT-решений: от разработки до запуска и поддержки
      </p>

      <div class="grid-3" v-if="services.length">
        <ServiceCard
          v-for="service in services"
          :key="service.id"
          :service="service"
        />
      </div>

      <p v-else class="text-center" style="color: var(--c-text-muted)">
        Загрузка услуг...
      </p>

      <!-- CTA -->
      <div class="services-cta text-center">
        <p class="services-cta__text">
          Не нашли нужную услугу? Мы подберём решение под ваш проект!
        </p>
        <button class="btn btn-primary" @click="openChat">
          💬 Обсудить проект
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
useHead({
  title: 'Услуги — Khudyakov Inc.',
  meta: [
    {
      name: 'description',
      content:
        'Веб-разработка, мобильные приложения, UI/UX дизайн, DevOps и IT-консалтинг от команды Khudyakov Inc.',
    },
  ],
})

const services = ref([])

const { data } = await useFetch('/api/services/')
if (data.value) {
  services.value = data.value
}

const openChat = () => {
  const toggle = document.getElementById('chat-toggle')
  if (toggle) toggle.click()
}
</script>

<style scoped>
.services-cta {
  margin-top: var(--space-4xl);
  padding: var(--space-3xl);
  background: var(--c-bg-card);
  border: 1px solid var(--c-border);
  border-radius: var(--radius-xl);
}

.services-cta__text {
  color: var(--c-text-secondary);
  font-size: 1.05rem;
  margin-bottom: var(--space-xl);
}
</style>
