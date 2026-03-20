<template>
  <div class="chat-widget">
    <!-- Proactive Toast (outside chat window) -->
    <Transition name="fade">
      <div v-if="proactiveGreeting && !isOpen" class="chat-proactive-toast glass" @click="toggleChat">
        <div class="chat-proactive-toast__close" @click.stop="proactiveGreeting = ''">✕</div>
        <div class="chat-proactive-toast__text">{{ proactiveGreeting }}</div>
      </div>
    </Transition>

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
        <!-- ── Header ─────────────────────── -->
        <div class="chat-header">
          <div class="chat-header__info">
            <div class="chat-header__avatar">
              <span class="chat-header__avatar-icon">🤖</span>
              <span class="chat-header__online-dot"></span>
            </div>
            <div>
              <div class="chat-header__title">AI-консультант</div>
              <div class="chat-header__status">Онлайн — отвечает мгновенно</div>
            </div>
          </div>
          <div class="chat-header__actions">
            <button class="chat-header__menu-btn" @click="showMenu = !showMenu" title="Меню">
              ⋮
            </button>
            <Transition name="fade">
              <div v-if="showMenu" class="chat-header__dropdown glass">
                <button @click="toggleLeadMode(); showMenu = false">
                  📝 {{ hasSubmittedLead ? 'Дополнить заявку' : 'Оставить заявку' }}
                </button>
                <button @click="toggleTrackingMode(); showMenu = false">
                  📋 Статус заявки
                </button>
                <button @click="clearChat(); showMenu = false">
                  🔄 Новый диалог
                </button>
              </div>
            </Transition>
          </div>
        </div>

        <!-- ── Messages Area ──────────────── -->
        <div class="chat-messages" ref="messagesContainer" @click="showMenu = false">
          <!-- ── Welcome Screen (no messages yet) ── -->
          <div v-if="messages.length === 0 && !isLoading" class="chat-welcome">
            <div class="chat-welcome__badge">⚡ Khudyakov Inc.</div>
            <h3 class="chat-welcome__title">Узнайте стоимость вашего проекта за 2 минуты</h3>
            <p class="chat-welcome__subtitle">
              AI-консультант поможет определить тип проекта, подходящие технологии и ориентировочную стоимость — без ожидания на линии.
            </p>
            <div class="chat-welcome__actions">
              <button class="chat-quick-btn" @click="quickAction('cost')">
                <span class="chat-quick-btn__icon">💰</span>
                <span>Узнать стоимость</span>
              </button>
              <button class="chat-quick-btn" @click="quickAction('design')">
                <span class="chat-quick-btn__icon">🎨</span>
                <span>Заказать дизайн</span>
              </button>
              <button class="chat-quick-btn" @click="quickAction('bot')">
                <span class="chat-quick-btn__icon">🤖</span>
                <span>Нужен бот</span>
              </button>
              <button class="chat-quick-btn" @click="quickAction('site')">
                <span class="chat-quick-btn__icon">🌐</span>
                <span>Сайт под ключ</span>
              </button>
            </div>
            <div class="chat-welcome__hint">
              Или просто напишите свой вопрос ниже ↓
            </div>
          </div>

          <!-- ── Chat Messages ── -->
          <template v-for="(msg, i) in messages" :key="i">
            <div
              class="chat-msg"
              :class="[
                msg.role === 'user' ? 'chat-msg--user' : 'chat-msg--bot',
                `chat-msg--anim-${i}`
              ]"
              :style="{ animationDelay: `${Math.min(i * 0.05, 0.3)}s` }"
            >
              <div v-if="msg.role !== 'user'" class="chat-msg__avatar-mini">🤖</div>
              <div class="chat-msg__bubble">{{ msg.text }}</div>
            </div>

            <!-- Quick suggestion chips after bot's first reply -->
            <div v-if="msg.role === 'assistant' && i === 0 && messages.length <= 2" class="chat-suggestions">
              <button
                v-for="chip in contextChips"
                :key="chip.label"
                class="chat-chip"
                @click="sendChip(chip.text)"
              >
                {{ chip.label }}
              </button>
            </div>
          </template>

          <!-- Typing indicator -->
          <div v-if="isLoading" class="chat-msg chat-msg--bot">
            <div class="chat-msg__avatar-mini">🤖</div>
            <div class="chat-msg__bubble chat-msg__typing">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>

        <!-- ── Lead Form ──────────────────── -->
        <div v-if="isLeadMode" class="chat-lead-form">
          <div class="chat-lead-form__icon">📝</div>
          <div class="chat-lead-form__title">{{ hasSubmittedLead ? 'Дополнить заявку' : 'Оставить заявку' }}</div>
          <p class="chat-lead-form__desc">Специалист свяжется в течение часа. История чата будет прикреплена.</p>
          <input v-model="leadForm.name" type="text" placeholder="Ваше имя" class="chat-input__field" />
          <input v-model="leadForm.contact" type="text" placeholder="Телефон или Telegram" class="chat-input__field" />
          <div class="chat-lead-form__actions">
            <button @click="toggleLeadMode" class="chat-btn chat-btn--secondary">Отмена</button>
            <button @click="submitLead" class="chat-btn chat-btn--primary" :disabled="isSubmittingLead || !leadForm.name || !leadForm.contact">
              {{ isSubmittingLead ? 'Отправка...' : '📨 Отправить' }}
            </button>
          </div>
        </div>

        <!-- ── Tracking Form ──────────────── -->
        <div v-else-if="isTrackingMode" class="chat-lead-form">
          <div class="chat-lead-form__icon">📋</div>
          <div class="chat-lead-form__title">Проверить статус заявки</div>
          <p class="chat-lead-form__desc">Введите телефон или почту, указанные при заявке</p>
          <input v-model="trackingContact" type="text" placeholder="Телефон или почта" class="chat-input__field" @keyup.enter="checkStatus" />
          <div v-if="trackingResult" class="tracking-result glass">
             <div class="tracking-result__status">Статус: <strong>{{ formatStatus(trackingResult.status) }}</strong></div>
             <div class="tracking-result__date">{{ formatDate(trackingResult.created_at) }}</div>
             <div v-if="trackingResult.status === 'completed'" class="mt-2 text-center">
                <a :href="`/api/leads/${trackingResult.id}/proposal`" target="_blank" class="chat-btn chat-btn--primary block text-center" style="text-decoration: none;">
                  📄 Скачать КП
                </a>
             </div>
          </div>
          <div class="chat-lead-form__actions">
            <button @click="isTrackingMode = false" class="chat-btn chat-btn--secondary">Назад</button>
            <button @click="checkStatus" class="chat-btn chat-btn--primary" :disabled="isCheckingStatus || !trackingContact">
              {{ isCheckingStatus ? 'Поиск...' : '🔍 Проверить' }}
            </button>
          </div>
        </div>

        <!-- ── Chat Input ─────────────────── -->
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

        <!-- ── Powered By Footer ──────────── -->
        <div class="chat-footer" v-if="!isLeadMode && !isTrackingMode">
          <span class="chat-footer__text">Khudyakov Inc. AI · Мгновенные ответы 24/7</span>
        </div>
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
const messagesContainer = ref(null)
const hasInteracted = ref(false)
const showMenu = ref(false)

// Lead Form State
const isLeadMode = ref(false)
const isSubmittingLead = ref(false)
const hasSubmittedLead = ref(false)
const leadForm = ref({ name: '', contact: '' })
const proactiveGreeting = ref('')

// Tracking State
const isTrackingMode = ref(false)
const isCheckingStatus = ref(false)
const trackingContact = ref('')
const trackingResult = ref(null)

// Context-aware suggestion chips (shown after first bot reply)
const contextChips = ref([
  { label: '💰 Сколько стоит?', text: 'Сколько примерно стоит разработка?' },
  { label: '⏱ Какие сроки?', text: 'Какие обычно сроки разработки?' },
  { label: '📋 Оставить заявку', text: 'заявка' },
])

const quickAction = (type) => {
  const quickMessages = {
    cost: 'Здравствуйте! Хочу узнать примерную стоимость проекта.',
    design: 'Здравствуйте! Меня интересует заказ дизайна.',
    bot: 'Здравствуйте! Мне нужен Telegram-бот.',
    site: 'Здравствуйте! Хочу заказать сайт под ключ.'
  }
  inputText.value = quickMessages[type] || ''
  sendMessage()
}

const sendChip = (text) => {
  if (text === 'заявка') {
    isLeadMode.value = true
    messages.value.push({ role: 'assistant', text: 'Отлично! Заполните форму ниже — ваш диалог будет прикреплён к заявке.' })
    scrollToBottom()
    return
  }
  inputText.value = text
  sendMessage()
}

const toggleTrackingMode = () => {
  isTrackingMode.value = !isTrackingMode.value
  isLeadMode.value = false
  trackingResult.value = null
  if (isTrackingMode.value) scrollToBottom()
}

const checkStatus = async () => {
  if (!trackingContact.value) return
  isCheckingStatus.value = true
  trackingResult.value = null
  try {
    const res = await $fetch(`/api/leads/status/check?contact=${encodeURIComponent(trackingContact.value)}`)
    trackingResult.value = res
  } catch (err) {
    alert("Заявка не найдена. Проверьте правильность введённых данных.")
  } finally {
    isCheckingStatus.value = false
  }
}

const formatStatus = (s) => {
  const map = {
    'new': '⏳ Новая',
    'in_progress': '⚙️ В работе',
    'completed': '✅ Завершена',
    'cancelled': '❌ Отменена'
  }
  return map[s] || s
}

const formatDate = (d) => new Date(d).toLocaleDateString('ru-RU')

// Lifecycle
onMounted(() => {
  // Restore chat state
  const savedState = localStorage.getItem('khudyakov_chat_state')
  if (savedState) {
    try {
      const parsed = JSON.parse(savedState)
      if (parsed.messages && Array.isArray(parsed.messages)) {
        messages.value = parsed.messages
        hasInteracted.value = parsed.messages.length > 0
        hasSubmittedLead.value = !!parsed.hasSubmittedLead
        if (parsed.leadForm) leadForm.value = parsed.leadForm
        scrollToBottom()
      }
    } catch (e) {}
  }

  // Proactive Triggers
  if (!hasInteracted.value) {
    // Time trigger — 12 seconds
    setTimeout(() => {
      if (!isOpen.value && !hasInteracted.value) {
        showProactiveGreeting("👋 Нужна помощь? Узнайте стоимость проекта за 2 минуты!")
      }
    }, 12000)

    // Scroll trigger
    const onScroll = () => {
      if (!isOpen.value && !hasInteracted.value && window.scrollY > 1200) {
        showProactiveGreeting("💡 Вижу, вы изучаете наши услуги. Рассчитать стоимость?")
        window.removeEventListener('scroll', onScroll)
      }
    }
    window.addEventListener('scroll', onScroll)

    // Exit intent trigger (desktop only)
    if (window.innerWidth > 768) {
      const onMouseLeave = (e) => {
        if (e.clientY < 5 && !isOpen.value && !hasInteracted.value) {
          showProactiveGreeting("🚀 Не уходите! Задайте вопрос — ответим мгновенно")
          document.removeEventListener('mouseleave', onMouseLeave)
        }
      }
      document.addEventListener('mouseleave', onMouseLeave)
    }
  }

  // Quiz context check
  const checkQuiz = () => {
     const quizData = localStorage.getItem('quiz_context')
     if (quizData && messages.value.length === 0) {
       if (isOpen.value) {
         try {
           const context = JSON.parse(quizData)
           sendMessage(null, context)
           localStorage.removeItem('quiz_context')
         } catch (e) {}
       }
     }
  }
  
  watch(isOpen, (val) => {
    if (val) {
      setTimeout(checkQuiz, 500)
    }
  })
  checkQuiz()
})

const showProactiveGreeting = (text) => {
  proactiveGreeting.value = text
  hasInteracted.value = false
}

const toggleChat = () => {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    hasInteracted.value = true
    proactiveGreeting.value = ''
    showMenu.value = false
  }
}

// Save to localStorage
watch([messages, hasSubmittedLead, leadForm], () => {
  localStorage.setItem('khudyakov_chat_state', JSON.stringify({
    messages: messages.value,
    hasSubmittedLead: hasSubmittedLead.value,
    leadForm: leadForm.value
  }))
}, { deep: true })

const clearChat = () => {
  messages.value = []
  hasInteracted.value = false
  hasSubmittedLead.value = false
  isLeadMode.value = false
  isTrackingMode.value = false
  leadForm.value = { name: '', contact: '' }
  localStorage.removeItem('khudyakov_chat_state')
  localStorage.removeItem('quiz_context')
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
  isTrackingMode.value = false
  if (isLeadMode.value) scrollToBottom()
}

const submitLead = async () => {
  if (!leadForm.value.name || !leadForm.value.contact) return
  isSubmittingLead.value = true
  let historyString = messages.value.map(m => `${m.role === 'user' ? 'Клиент' : 'ИИ'}: ${m.text}`).join('\n\n')
  try {
    await $fetch('/api/leads/', {
      method: 'POST',
      body: { ...leadForm.value, chat_history: historyString, is_supplement: hasSubmittedLead.value }
    })
    const wasSupplement = hasSubmittedLead.value
    isLeadMode.value = false
    hasSubmittedLead.value = true
    messages.value.push({ role: 'assistant', text: wasSupplement ? '✅ Дополнение отправлено! Менеджер получит обновлённую информацию.' : '✅ Спасибо! Ваши контакты переданы команде. Специалист свяжется в течение часа.' })
    scrollToBottom()
  } catch (err) {
    messages.value.push({ role: 'assistant', text: '❌ Ошибка при отправке заявки. Попробуйте ещё раз.' })
  } finally {
    isSubmittingLead.value = false
  }
}

const sendMessage = async (e, quizContext = null) => {
  let text = inputText.value.trim()
  
  if (quizContext) {
    text = `Привет! Я прошел квиз на вашем сайте. Мой проект: ${quizContext.type}. По дизайну: ${quizContext.design}. Ожидаемые сроки: ${quizContext.timeline}. Что скажете, какие будут этапы и примерная стоимость?`
  }

  if (!text || isLoading.value) return

  hasInteracted.value = true
  messages.value.push({ role: 'user', text: quizContext ? `Обсудим проект: ${quizContext.type}` : text })
  inputText.value = ''
  isLoading.value = true
  scrollToBottom()

  // Handle local text commands
  const lowerText = text.toLowerCase()
  const cleanText = lowerText.replace(/\s+/g, '')

  if (cleanText.includes('оставитьзаявку') || cleanText === 'заявка') {
    isLeadMode.value = true
    messages.value.push({ role: 'assistant', text: 'Отлично! Заполните форму ниже — ваш диалог будет прикреплён к заявке.' })
    isLoading.value = false
    scrollToBottom()
    return
  }

  if (cleanText.includes('отследитьзаявку')) {
    isTrackingMode.value = true
    messages.value.push({ role: 'assistant', text: 'Введите контактные данные для проверки статуса.' })
    isLoading.value = false
    scrollToBottom()
    return
  }

  if (cleanText.includes('новыйчат') || cleanText.includes('очиститьчат')) {
    clearChat()
    isLoading.value = false
    return
  }

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
        has_submitted_lead: hasSubmittedLead.value,
        quiz_context: quizContext
      },
    })

    messages.value.push({ role: 'assistant', text: response.reply })
  } catch (err) {
    messages.value.push({ role: 'assistant', text: 'Ошибка соединения. Попробуйте позже.' })
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
  width: 62px;
  height: 62px;
  border-radius: 50%;
  background: var(--c-gradient-1);
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 24px var(--c-accent-glow);
  transition: all var(--duration-normal) var(--ease-out);
  position: relative;
}

.chat-toggle:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 32px var(--c-accent-glow);
}

.chat-toggle.active {
  background: var(--c-bg-secondary);
  border: 1px solid var(--c-border);
  box-shadow: var(--shadow-card);
}

.chat-toggle__icon {
  font-size: 1.6rem;
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
  top: -2px;
  right: -2px;
  width: 16px;
  height: 16px;
  background: #ff4d4f;
  border: 2px solid var(--c-bg-secondary);
  border-radius: 50%;
  animation: bounceDot 1.5s ease-in-out infinite;
}

@keyframes bounceDot {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.3); box-shadow: 0 0 12px #ff4d4f; }
}

@keyframes pulseGlow {
  0% { transform: scale(1); opacity: 0.6; }
  100% { transform: scale(1.35); opacity: 0; }
}

/* ── Chat Window ──────────────────────── */
.chat-window {
  position: absolute;
  bottom: 80px;
  right: 0;
  width: clamp(360px, 28vw, 520px);
  height: clamp(520px, 68vh, 800px);
  border-radius: var(--radius-xl);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: var(--shadow-modal);
  border: 1px solid var(--c-border);
}

/* ── Header ───────────────────────────── */
.chat-header {
  padding: 0.9rem 1rem;
  border-bottom: 1px solid var(--c-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--c-bg-secondary);
}

.chat-header__info {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.chat-header__avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--c-gradient-1);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  flex-shrink: 0;
}

.chat-header__avatar-icon {
  font-size: 1.1rem;
}

.chat-header__online-dot {
  position: absolute;
  bottom: -1px;
  right: -1px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--c-success);
  border: 2px solid var(--c-bg-secondary);
  box-shadow: 0 0 6px var(--c-success);
}

.chat-header__title {
  font-weight: 700;
  font-size: 0.92rem;
  letter-spacing: -0.01em;
}

.chat-header__status {
  font-size: 0.7rem;
  color: var(--c-text-muted);
}

.chat-header__actions {
  position: relative;
}

.chat-header__menu-btn {
  background: none;
  border: none;
  color: var(--c-text-primary);
  font-size: 1.4rem;
  cursor: pointer;
  padding: 0.3rem 0.5rem;
  border-radius: var(--radius-sm);
  transition: background 0.15s;
  letter-spacing: 1px;
}

.chat-header__menu-btn:hover {
  background: var(--c-bg-tertiary);
}

.chat-header__dropdown {
  position: absolute;
  top: calc(100% + 6px);
  right: 0;
  min-width: 180px;
  padding: 0.4rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--c-border);
  z-index: 10;
  display: flex;
  flex-direction: column;
}

.chat-header__dropdown button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.55rem 0.7rem;
  background: none;
  border: none;
  color: var(--c-text-primary);
  font-size: 0.82rem;
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: background 0.15s;
  text-align: left;
  white-space: nowrap;
}

.chat-header__dropdown button:hover {
  background: var(--c-bg-tertiary);
}

/* ── Messages ─────────────────────────── */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  scroll-behavior: smooth;
}

/* ── Welcome Screen ───────────────────── */
.chat-welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 1.2rem 0.5rem;
  gap: 0.8rem;
  animation: welcomeFadeIn 0.6s var(--ease-out);
}

@keyframes welcomeFadeIn {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}

.chat-welcome__badge {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.3rem 0.8rem;
  background: var(--c-bg-card);
  border: 1px solid var(--c-accent);
  border-radius: var(--radius-full);
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--c-accent);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.chat-welcome__title {
  font-size: 1.15rem;
  font-weight: 700;
  line-height: 1.3;
  color: var(--c-text-primary);
  margin: 0;
}

.chat-welcome__subtitle {
  font-size: 0.82rem;
  color: var(--c-text-muted);
  line-height: 1.5;
  margin: 0;
  max-width: 300px;
}

.chat-welcome__actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
  width: 100%;
  margin-top: 0.3rem;
}

.chat-quick-btn {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.6rem 0.7rem;
  background: var(--c-bg-card);
  border: 1px solid var(--c-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: 0.78rem;
  color: var(--c-text-primary);
  transition: all 0.2s var(--ease-out);
  text-align: left;
}

.chat-quick-btn:hover {
  border-color: var(--c-accent);
  background: var(--c-bg-tertiary);
  transform: translateY(-1px);
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.chat-quick-btn__icon {
  font-size: 1.1rem;
  flex-shrink: 0;
}

.chat-welcome__hint {
  font-size: 0.72rem;
  color: var(--c-text-muted);
  opacity: 0.7;
  margin-top: 0.2rem;
}

/* ── Chat Messages ────────────────────── */
.chat-msg {
  display: flex;
  align-items: flex-end;
  gap: 0.4rem;
  animation: msgSlideIn 0.3s var(--ease-out) both;
}

@keyframes msgSlideIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.chat-msg--user {
  justify-content: flex-end;
}

.chat-msg__avatar-mini {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--c-gradient-1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  flex-shrink: 0;
}

.chat-msg__bubble {
  max-width: 82%;
  padding: 0.7rem 1rem;
  border-radius: var(--radius-md);
  font-size: clamp(0.84rem, 0.9vw, 1rem);
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
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

/* ── Suggestion Chips ─────────────────── */
.chat-suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  padding-left: 2rem;
  animation: msgSlideIn 0.4s var(--ease-out) 0.2s both;
}

.chat-chip {
  padding: 0.35rem 0.7rem;
  background: var(--c-bg-card);
  border: 1px solid var(--c-border);
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  color: var(--c-text-primary);
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.chat-chip:hover {
  border-color: var(--c-accent);
  background: var(--c-bg-tertiary);
  color: var(--c-accent);
}

/* ── Typing indicator ─────────────────── */
.chat-msg__typing {
  display: flex;
  gap: 4px;
  padding: 0.9rem 1.1rem;
}

.chat-msg__typing span {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--c-text-muted);
  animation: typing 1.2s infinite;
}

.chat-msg__typing span:nth-child(2) { animation-delay: 0.2s; }
.chat-msg__typing span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 60%, 100% { opacity: 0.3; transform: translateY(0); }
  30% { opacity: 1; transform: translateY(-4px); }
}

/* ── Inputs & Forms ───────────────────── */
.chat-input {
  display: flex;
  padding: 0.6rem 0.8rem;
  border-top: 1px solid var(--c-border);
  gap: 0.5rem;
  align-items: center;
}

.chat-lead-form {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 1rem;
  border-top: 1px solid var(--c-border);
  background: var(--c-bg-secondary);
  animation: formSlideUp 0.3s var(--ease-out);
}

@keyframes formSlideUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.chat-lead-form__icon {
  font-size: 1.5rem;
  text-align: center;
}

.chat-lead-form__title {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--c-text-primary);
  text-align: center;
}

.chat-lead-form__desc {
  font-size: 0.75rem;
  color: var(--c-text-muted);
  text-align: center;
  margin: 0;
  line-height: 1.4;
}

.chat-lead-form__actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.3rem;
}

.chat-input__field {
  flex: 1;
  background: var(--c-bg-card);
  border: 1px solid var(--c-border);
  border-radius: var(--radius-full);
  padding: 0.6rem 1rem;
  color: var(--c-text-primary);
  font-family: var(--font-main);
  font-size: 0.85rem;
  outline: none;
  transition: border-color 0.2s;
}

.chat-input__field:focus {
  border-color: var(--c-accent);
}

.chat-input__field::placeholder {
  color: var(--c-text-muted);
}

.chat-input__send {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: var(--c-gradient-1);
  border: none;
  color: #fff;
  font-size: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s var(--ease-out);
  flex-shrink: 0;
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
  padding: 0.55rem;
  border-radius: var(--radius-full);
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.chat-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.chat-btn--primary {
  background: var(--c-gradient-1);
  color: #fff;
}

.chat-btn--primary:not(:disabled):hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

.chat-btn--secondary {
  background: transparent;
  border: 1px solid var(--c-border);
  color: var(--c-text-primary);
}

.chat-btn--secondary:hover {
  background: var(--c-bg-tertiary);
}

/* ── Footer ───────────────────────────── */
.chat-footer {
  padding: 0.4rem 0.8rem;
  border-top: 1px solid var(--c-border);
  text-align: center;
  background: var(--c-bg-secondary);
}

.chat-footer__text {
  font-size: 0.65rem;
  color: var(--c-text-muted);
  opacity: 0.7;
}

/* ── Tracking Result ──────────────────── */
.tracking-result {
  padding: 0.8rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--c-border);
  text-align: center;
}

.tracking-result__status {
  font-size: 1rem;
  margin-bottom: 0.2rem;
}

.tracking-result__date {
  font-size: 0.72rem;
  color: var(--c-text-muted);
}

/* ── Slide Transition ─────────────────── */
.chat-slide-enter-active,
.chat-slide-leave-active {
  transition: all var(--duration-normal) var(--ease-spring);
}

.chat-slide-enter-from,
.chat-slide-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.92);
}

/* ── Proactive Toast ──────────────────── */
.chat-proactive-toast {
  position: absolute;
  bottom: 10px;
  right: 74px;
  width: 250px;
  padding: 0.9rem 1rem;
  border-radius: var(--radius-lg);
  border: 1px solid var(--c-border);
  cursor: pointer;
  z-index: 1000;
  animation: slideInRight 0.5s var(--ease-spring);
}

.chat-proactive-toast__text {
  font-size: 0.82rem;
  line-height: 1.45;
  color: var(--c-text-primary);
}

.chat-proactive-toast__close {
  position: absolute;
  top: 5px;
  right: 8px;
  font-size: 0.7rem;
  opacity: 0.5;
  padding: 4px;
  cursor: pointer;
}

@keyframes slideInRight {
  from { opacity: 0; transform: translateX(20px); }
  to { opacity: 1; transform: translateX(0); }
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.block { display: block; }
.mt-2 { margin-top: 0.5rem; }
.text-center { text-align: center; }

/* ── Responsive ───────────────────────── */
@media (max-width: 480px) {
  .chat-widget {
    bottom: var(--space-md);
    right: var(--space-md);
  }
  
  .chat-toggle {
    width: 54px;
    height: 54px;
  }

  .chat-window {
    width: calc(100vw - 2rem);
    height: calc(100dvh - 120px);
    bottom: 68px;
    right: 0;
  }

  .chat-welcome__actions {
    grid-template-columns: 1fr;
  }

  .chat-welcome__title {
    font-size: 1.05rem;
  }
}

@media (min-width: 1600px) {
  .chat-header__title {
    font-size: 1.05rem;
  }
  .chat-input__field {
    font-size: 0.95rem;
    padding: 0.75rem 1.1rem;
  }
}
</style>
