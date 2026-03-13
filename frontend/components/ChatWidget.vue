<template>
  <div class="chat-widget">
    <!-- Toggle Button -->
    <button class="chat-toggle" :class="{ active: isOpen }" @click="toggleChat" id="chat-toggle">
      <span class="chat-toggle__icon" v-if="!isOpen">💬</span>
      <span class="chat-toggle__icon chat-toggle__icon--close" v-else>✕</span>
      <span class="chat-toggle__pulse" v-if="!isOpen && !hasInteracted"></span>
      <span class="chat-toggle__dot" v-if="!isOpen && !hasInteracted"></span>
    </button>

    <!-- Chat Window -->
    <Transition name="chat-slide">
      <div v-if="isOpen" class="chat-window glass" id="chat-window">
        <div class="chat-header">
          <div class="chat-header__info">
            <div class="chat-header__dot"></div>
            <div>
              <div class="chat-header__title">Khudyakov Inc. AI</div>
              <div class="chat-header__status">Онлайн — готов помочь</div>
            </div>
          </div>
          <div style="display: flex; gap: 0.5rem; align-items: center;">
            <button class="chat-header__icon-btn" @click="clearChat" title="Начать новый диалог">
              🔄
            </button>
            <button class="chat-header__lead-btn" @click="toggleLeadMode" :title="hasSubmittedLead ? 'Дополнить заявку' : 'Оставить контакты'">
              {{ hasSubmittedLead ? '📝 Дополнить' : '☎️ Заявка' }}
            </button>
          </div>
        </div>

        <div class="chat-messages" ref="messagesContainer">
          <!-- Welcome message -->
          <div class="chat-msg chat-msg--bot" v-if="messages.length === 0">
            <div class="chat-msg__bubble">
              Привет! 👋 Я IT-эксперт студии <strong>Khudyakov Inc.</strong>
              Расскажите, что вы хотите создать? Мы делаем всё: от сайтов и мобильных приложений до дизайна логотипов и Telegram-ботов. Я помогу сориентироваться по технологиям и сориентирую по этапам!
            </div>
          </div>

          <div
            v-for="(msg, i) in messages"
            :key="i"
            class="chat-msg"
            :class="msg.role === 'user' ? 'chat-msg--user' : 'chat-msg--bot'"
          >
            <div class="chat-msg__bubble">{{ msg.text }}</div>
          </div>

          <!-- Typing indicator -->
          <div v-if="isLoading" class="chat-msg chat-msg--bot">
            <div class="chat-msg__bubble chat-msg__typing">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>

        <!-- Lead Form -->
        <div v-if="isLeadMode" class="chat-lead-form">
          <div class="chat-lead-form__title">{{ hasSubmittedLead ? 'Дополнить заявку (будет прикреплено)' : 'Оставить заявку (диалог прикрепится)' }}</div>
          <input v-model="leadForm.name" type="text" placeholder="Ваше имя" class="chat-input__field mb-2" />
          <input v-model="leadForm.contact" type="text" placeholder="Телефон или Telegram" class="chat-input__field mb-2" />
          <div class="chat-lead-form__actions">
            <button @click="toggleLeadMode" class="chat-btn chat-btn--secondary">Отмена</button>
            <button @click="submitLead" class="chat-btn chat-btn--primary" :disabled="isSubmittingLead || !leadForm.name || !leadForm.contact">
              {{ isSubmittingLead ? 'Отправка...' : 'Отправить' }}
            </button>
          </div>
        </div>

        <!-- Chat Input -->
        <form v-else class="chat-input" @submit.prevent="sendMessage">
          <input
            v-model="inputText"
            type="text"
            placeholder="Напишите сообщение..."
            :disabled="isLoading"
            class="chat-input__field"
            id="chat-input-field"
          />
          <button type="submit" class="chat-input__send" :disabled="!inputText.trim() || isLoading">
            ➤
          </button>
        </form>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'

const isOpen = ref(false)
const inputText = ref('')
const messages = ref([])
const isLoading = ref(false)
const hasInteracted = ref(false)
const messagesContainer = ref(null)

// Lead Form State
const isLeadMode = ref(false)
const isSubmittingLead = ref(false)
const hasSubmittedLead = ref(false)
const leadForm = ref({ name: '', contact: '' })

// Sound effect
const playNotificationSound = () => {
  try {
    const audio = new Audio('https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3')
    audio.volume = 0.5
    audio.play().catch(e => console.warn("Autoplay blocked:", e))
  } catch (e) {
    console.error("Failed to play sound", e)
  }
}

// Lifecycle
onMounted(() => {
  // Restore chat state from localStorage
  const savedState = localStorage.getItem('khudyakov_chat_state')
  if (savedState) {
    try {
      const parsed = JSON.parse(savedState)
      if (parsed.messages && Array.isArray(parsed.messages)) {
        messages.value = parsed.messages
        hasInteracted.value = parsed.messages.length > 0
        hasSubmittedLead.value = !!parsed.hasSubmittedLead
        if (parsed.leadForm) {
          leadForm.value = parsed.leadForm
        }
        scrollToBottom()
      }
    } catch (e) {
      console.error("Failed to parse chat state", e)
    }
  } else {
    // Migration from old basic history
    const oldHistory = localStorage.getItem('khudyakov_chat_history')
    if (oldHistory) {
      try {
        const parsed = JSON.parse(oldHistory)
        if (Array.isArray(parsed)) {
          messages.value = parsed
          hasInteracted.value = parsed.length > 0
          scrollToBottom()
        }
      } catch (e) {}
    }
  }

  // Attention seeking mechanism
  if (!hasInteracted.value) {
    setTimeout(() => {
      if (!isOpen.value && !hasInteracted.value) {
        playNotificationSound()
      }
    }, 3000)
  }
})

const toggleChat = () => {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    hasInteracted.value = true
  }
}

// Save to localStorage continuously
watch([messages, hasSubmittedLead, leadForm], () => {
  localStorage.setItem('khudyakov_chat_state', JSON.stringify({
    messages: messages.value,
    hasSubmittedLead: hasSubmittedLead.value,
    leadForm: leadForm.value
  }))
}, { deep: true })

const clearChat = () => {
  if (confirm("Вы уверены, что хотите начать новый диалог? Текущая история будет очищена.")) {
    messages.value = []
    hasInteracted.value = false
    hasSubmittedLead.value = false
    isLeadMode.value = false
    leadForm.value = { name: '', contact: '' }
    localStorage.removeItem('khudyakov_chat_state')
    localStorage.removeItem('khudyakov_chat_history')
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const toggleLeadMode = () => {
  isLeadMode.value = !isLeadMode.value
  if (isLeadMode.value) {
    scrollToBottom()
  }
}

const submitLead = async () => {
  if (!leadForm.value.name || !leadForm.value.contact) return
  isSubmittingLead.value = true

  // Format chat history as a readable string
  let historyString = messages.value.map(m => {
    const roleName = m.role === 'user' ? 'Клиент' : 'ИИ-Менеджер'
    return `${roleName}: ${m.text}`
  }).join('\n\n')

  try {
    await $fetch('/api/leads/', {
      method: 'POST',
      body: {
        name: leadForm.value.name,
        contact: leadForm.value.contact,
        chat_history: historyString,
        is_supplement: hasSubmittedLead.value
      }
    })
    
    // Success feedback
    const wasSupplement = hasSubmittedLead.value
    isLeadMode.value = false
    hasSubmittedLead.value = true
    
    if (wasSupplement) {
      messages.value.push({ role: 'assistant', text: '✅ Дополнение успешно отправлено! Мы прикрепили его к вашей заявке.' })
    } else {
      messages.value.push({ role: 'assistant', text: '✅ Спасибо! Ваши контакты и наша переписка успешно переданы команде. Если у вас появятся новые вопросы или детали проекта, пишите сюда, а затем нажмите кнопку "📝 Дополнить".' })
    }
    scrollToBottom()
  } catch (err) {
    messages.value.push({ role: 'assistant', text: '❌ Ошибка при отправке заявки. Пожалуйста, напишите нам в Telegram напрямую.' })
  } finally {
    isSubmittingLead.value = false
  }
}

const sendMessage = async () => {
  const text = inputText.value.trim()
  if (!text || isLoading.value) return

  hasInteracted.value = true
  messages.value.push({ role: 'user', text })
  inputText.value = ''
  isLoading.value = true
  scrollToBottom()

  try {
    const history = messages.value.slice(0, -1).map((m) => ({
      role: m.role === 'user' ? 'user' : 'assistant',
      text: m.text,
    }))

    const response = await $fetch('/api/chat/', {
      method: 'POST',
      body: { 
        message: text, 
        history,
        has_submitted_lead: hasSubmittedLead.value 
      },
    })

    messages.value.push({ role: 'assistant', text: response.reply })
  } catch (err) {
    messages.value.push({
      role: 'assistant',
      text: 'Извините, произошла ошибка. Попробуйте позже или свяжитесь с нами напрямую.',
    })
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}
</script>

<style scoped>
.chat-widget {
  position: fixed;
  bottom: var(--space-xl);
  right: var(--space-xl);
  z-index: 999;
}

/* ── Toggle Button ────────────────────── */
.chat-toggle {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: var(--c-gradient-1);
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 20px var(--c-accent-glow);
  transition: all var(--duration-normal) var(--ease-out);
  position: relative;
}

.chat-toggle:hover {
  transform: scale(1.08);
  box-shadow: 0 6px 30px var(--c-accent-glow);
}

.chat-toggle.active {
  background: var(--c-bg-secondary);
  border: 1px solid var(--c-border);
  box-shadow: var(--shadow-card);
}

.chat-toggle__icon {
  font-size: 1.5rem;
}

.chat-toggle__icon--close {
  color: var(--c-accent);
  font-weight: bold;
  font-size: 1.8rem;
}

.chat-toggle__pulse {
  position: absolute;
  inset: -4px;
  border-radius: 50%;
  border: 2px solid var(--c-accent);
  animation: pulseGlow 2s ease-in-out infinite;
  pointer-events: none;
}

.chat-toggle__dot {
  position: absolute;
  top: 0;
  right: 0;
  width: 14px;
  height: 14px;
  background: #ff4d4f;
  border: 2px solid var(--c-bg-secondary);
  border-radius: 50%;
  animation: bounceDot 1.5s ease-in-out infinite;
}

@keyframes bounceDot {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.3); box-shadow: 0 0 10px #ff4d4f; }
}

@keyframes pulseGlow {
  0% { transform: scale(1); opacity: 0.6; }
  100% { transform: scale(1.3); opacity: 0; }
}

/* ── Chat Window ──────────────────────── */
.chat-window {
  position: absolute;
  bottom: 76px;
  right: 0;
  width: 380px;
  height: 520px;
  border-radius: var(--radius-xl);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: var(--shadow-modal);
}

.chat-header {
  padding: var(--space-lg);
  border-bottom: 1px solid var(--c-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-header__info {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.chat-header__dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--c-success);
  box-shadow: 0 0 8px var(--c-success);
  flex-shrink: 0;
}

.chat-header__title {
  font-weight: 600;
  font-size: 0.95rem;
}

.chat-header__status {
  font-size: 0.75rem;
  color: var(--c-text-muted);
}

.chat-header__lead-btn {
  background: var(--c-bg-tertiary);
  border: 1px solid var(--c-border);
  color: var(--c-text-primary);
  padding: 0.3rem 0.6rem;
  border-radius: var(--radius-sm);
  font-size: 0.8rem;
  cursor: pointer;
  transition: all var(--duration-fast);
}

.chat-header__lead-btn:hover {
  background: var(--c-accent);
  color: #fff;
  border-color: var(--c-accent);
}

/* ── Messages ─────────────────────────── */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-lg);
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.chat-msg {
  display: flex;
}

.chat-msg--user {
  justify-content: flex-end;
}

.chat-msg__bubble {
  max-width: 80%;
  padding: 0.7rem 1rem;
  border-radius: var(--radius-md);
  font-size: 0.88rem;
  line-height: 1.5;
  white-space: pre-wrap;
}

.chat-msg--bot .chat-msg__bubble {
  background: var(--c-bg-card);
  border: 1px solid var(--c-border);
  color: var(--c-text-primary);
  border-bottom-left-radius: 4px;
}

.chat-msg--user .chat-msg__bubble {
  background: var(--c-gradient-1);
  color: #fff;
  border-bottom-right-radius: 4px;
}

/* ── Typing indicator ─────────────────── */
.chat-msg__typing {
  display: flex;
  gap: 4px;
  padding: 1rem 1.2rem;
}

.chat-msg__typing span {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--c-text-muted);
  animation: typing 1.2s infinite;
}

.chat-msg__typing span:nth-child(2) {
  animation-delay: 0.2s;
}

.chat-msg__typing span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% { opacity: 0.3; transform: translateY(0); }
  30% { opacity: 1; transform: translateY(-4px); }
}

/* ── Inputs & Forms ───────────────────── */
.chat-input, .chat-lead-form {
  display: flex;
  padding: var(--space-md);
  border-top: 1px solid var(--c-border);
  gap: var(--space-sm);
}

.chat-lead-form {
  flex-direction: column;
  background: var(--c-bg-secondary);
}

.chat-lead-form__title {
  font-size: 0.85rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--c-text-primary);
  text-align: center;
}

.chat-lead-form__actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.mb-2 {
  margin-bottom: 0.5rem;
}

.chat-input__field {
  flex: 1;
  background: var(--c-bg-card);
  border: 1px solid var(--c-border);
  border-radius: var(--radius-full);
  padding: 0.6rem 1rem;
  color: var(--c-text-primary);
  font-family: var(--font-main);
  font-size: 0.88rem;
  outline: none;
  transition: border-color var(--duration-fast);
}

.chat-input__field:focus {
  border-color: var(--c-accent);
}

.chat-input__field::placeholder {
  color: var(--c-text-muted);
}

.chat-input__send {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--c-gradient-1);
  border: none;
  color: #fff;
  font-size: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--duration-fast) var(--ease-out);
}

.chat-input__send:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.chat-input__send:not(:disabled):hover {
  transform: scale(1.08);
}

.chat-btn {
  flex: 1;
  padding: 0.6rem;
  border-radius: var(--radius-full);
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: opacity 0.2s;
}

.chat-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.chat-btn--primary {
  background: var(--c-gradient-1);
  color: #fff;
}

.chat-btn--secondary {
  background: transparent;
  border: 1px solid var(--c-border);
  color: var(--c-text-primary);
}

/* ── Slide transition ─────────────────── */
.chat-slide-enter-active,
.chat-slide-leave-active {
  transition: all var(--duration-normal) var(--ease-spring);
}

.chat-slide-enter-from,
.chat-slide-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.92);
}

/* ── Responsive ───────────────────────── */
@media (max-width: 480px) {
  .chat-widget {
    bottom: var(--space-md);
    right: var(--space-md);
  }

  .chat-window {
    width: calc(100vw - 2rem);
    right: -0.5rem;
    height: 70vh;
  }
}
</style>
