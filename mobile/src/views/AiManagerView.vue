<template>
  <div class="view-container">
    <header class="view-header">
      <h2>🤖 AI Менеджер</h2>
    </header>

    <div class="view-content">
      <!-- Evaluate Order -->
      <div class="ai-card">
        <h3>📊 Оценка заказа</h3>
        <p class="subtitle">Вставьте текст клиента для расчета стоимости</p>
        <textarea v-model="orderText" class="input-field ai-textarea" placeholder="Запрос клиента..." rows="4"></textarea>
        <button class="btn btn-primary mt-sm w-100" @click="evaluateOrder" :disabled="loadingOrder">
          {{ loadingOrder ? 'Думаю...' : 'Оценить стоимость' }}
        </button>
        <div v-if="orderResult" class="ai-result mt-sm">
          {{ orderResult }}
        </div>
      </div>

      <!-- General Question -->
      <div class="ai-card mt-md">
        <h3>💬 Вопрос ИИ</h3>
        <p class="subtitle">База знаний, цены, процессы</p>
        <textarea v-model="questionText" class="input-field ai-textarea" placeholder="Спросите меня..." rows="3"></textarea>
        <button class="btn btn-primary mt-sm w-100" @click="askQuestion" :disabled="loadingQuestion">
          {{ loadingQuestion ? 'Думаю...' : 'Спросить' }}
        </button>
        <div v-if="questionResult" class="ai-result mt-sm">
          {{ questionResult }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { api } from '../api.js'

const orderText = ref('')
const orderResult = ref('')
const loadingOrder = ref(false)

const questionText = ref('')
const questionResult = ref('')
const loadingQuestion = ref(false)

async function evaluateOrder() {
  if (!orderText.value.trim()) return
  loadingOrder.value = true
  orderResult.value = ''
  try {
    const res = await api.evaluateOrder(orderText.value)
    orderResult.value = res.result
  } catch (e) {
    alert(e.message)
  } finally {
    loadingOrder.value = false
  }
}

async function askQuestion() {
  if (!questionText.value.trim()) return
  loadingQuestion.value = true
  questionResult.value = ''
  try {
    const res = await api.askAiQuestion(questionText.value)
    questionResult.value = res.result
  } catch (e) {
    alert(e.message)
  } finally {
    loadingQuestion.value = false
  }
}
</script>

<style scoped>
.ai-card {
  background: var(--surface);
  border-radius: 12px;
  padding: 1rem;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.ai-textarea {
  width: 100%;
  margin-top: 0.5rem;
  background: var(--bg);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.5rem;
}
.subtitle {
  font-size: 0.8rem;
  color: #888;
  margin-top: -0.5rem;
}
.ai-result {
  margin-top: 1rem;
  padding: 1rem;
  background: rgba(46, 213, 115, 0.1);
  border-left: 3px solid #2ed573;
  border-radius: 4px;
  font-size: 0.9rem;
  white-space: pre-wrap;
}
.w-100 { width: 100%; }
.mt-sm { margin-top: 0.5rem; }
.mt-md { margin-top: 1rem; }
</style>
