<template>
  <div class="section">
    <div class="container">
      <h1 class="section__title">Портфолио</h1>
      <p class="section__subtitle">
        Реальные проекты, которые мы создали для наших клиентов
      </p>

      <div class="grid-3" v-if="projects.length">
        <PortfolioCard
          v-for="project in projects"
          :key="project.id"
          :project="project"
        />
      </div>

      <p v-else class="text-center" style="color: var(--c-text-muted)">
        Загрузка портфолио...
      </p>
    </div>
  </div>
</template>

<script setup>
useHead({
  title: 'Портфолио — Khudyakov Inc.',
  meta: [
    {
      name: 'description',
      content: 'Примеры работ команды Khudyakov Inc.: веб-приложения, мобильные приложения, CRM-системы и другие IT-решения.',
    },
  ],
})

const projects = ref([])

const { data } = await useFetch('/api/portfolio/')
if (data.value) {
  projects.value = data.value
}
</script>
