<script setup>
import { ref, nextTick, watch } from 'vue';

// --- STATO DELL'APPLICAZIONE ---
const userInput = ref('');
const isChatActive = ref(false);
const isTyping = ref(false);
const messagesContainer = ref(null);

// Cronologia messaggi
const messages = ref([]);

// --- LOGICA ---

// 1. "Effetto Gemini": Appena l'utente scrive, nasconde il benvenuto
watch(userInput, (newVal) => {
  if (newVal.trim().length > 0 && !isChatActive.value) {
    startChatSession();
  }
});

const startChatSession = () => {
  isChatActive.value = true;
  // Focus e scroll
  nextTick(() => {
    scrollToBottom();
  });
};

// 2. Invio Messaggio
const sendMessage = () => {
  const text = userInput.value.trim();
  if (!text) return;

  // Aggiungi messaggio utente
  messages.value.push({
    id: Date.now(),
    text: text,
    sender: 'user'
  });

  userInput.value = '';
  scrollToBottom();

  // Simula risposta Bot
  isTyping.value = true;

  setTimeout(() => {
    isTyping.value = false;
    
    const risposte = [
      "Sto elaborando la tua richiesta con i dati disponibili.",
      "Interessante. Ecco cosa ho trovato nei miei archivi.",
      "Posso aiutarti a espandere questo concetto.",
      "Ho generato una risposta basata sul contesto fornito."
    ];
    
    messages.value.push({
      id: Date.now() + 1,
      text: risposte[Math.floor(Math.random() * risposte.length)],
      sender: 'bot'
    });
    
    scrollToBottom();
  }, 1500);
};

// Utility Scroll
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
      // Fallback per scroll finestra
      window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
    }
  });
};
</script>

<template>
  <div class="app-container">
    
    <header class="chat-header">
      <div class="brand">
        <svg class="logo-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"></circle>
          <path d="M12 16v-4"></path>
          <path d="M12 8h.01"></path>
        </svg>
        <span>Nexus AI</span>
      </div>
    </header>

    <main class="main-area">
      
      <transition name="fade-up">
        <div v-if="!isChatActive" class="welcome-container">
          <div class="welcome-content">
            <h1 class="gradient-title">Ciao!</h1>
            <h2 class="subtitle-text">Come posso esserti utile oggi?</h2>
          </div>
        </div>
      </transition>

      <transition name="fade-in">
        <div v-show="isChatActive" class="chat-messages" ref="messagesContainer">
          <div class="messages-inner">
            <div 
              v-for="msg in messages" 
              :key="msg.id" 
              class="message" 
              :class="msg.sender"
            >
              {{ msg.text }}
            </div>
          </div>
        </div>
      </transition>

    </main>

    <footer class="footer-area">
      <div class="footer-content">
        <transition name="fade">
          <div v-if="isTyping" class="status-indicator">
            <span class="sparkle">✨</span>
            <span>Nexus sta scrivendo...</span>
          </div>
        </transition>

        <div class="input-wrapper" :class="{ 'focused': userInput.length > 0 }">
          <input 
            type="text" 
            v-model="userInput" 
            @keydown.enter="sendMessage"
            placeholder="Chiedi qualsiasi cosa..." 
            autocomplete="off"
          >
          <button class="send-btn" @click="sendMessage">
            <svg class="send-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="5" y1="12" x2="19" y2="12"></line>
              <polyline points="12 5 19 12 12 19"></polyline>
            </svg>
          </button>
        </div>
      </div>
    </footer>

  </div>
</template>

<style scoped>
.app-container {
  --bg-color: #050505;
  --text-primary: #ffffff;
  --text-secondary: #888888;
  --msg-bot-bg: #141414;
  --msg-user-bg: #262626;
  --accent-color: #4f46e5;
  --accent-glow: rgba(79, 70, 229, 0.4);
  --input-bg: rgba(20, 20, 20, 0.9);
  --input-border: rgba(255, 255, 255, 0.1);

  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  height: 100vh;
  width: 100vw;
  background-color: var(--bg-color);
  background-image: radial-gradient(circle at 50% 0%, #1a1a2e 0%, var(--bg-color) 60%);
  color: var(--text-primary);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-header {
  height: 80px;
  padding: 0 40px;
  display: flex;
  align-items: center;
  flex-shrink: 0;
  z-index: 10;
}
.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 500;
  font-size: 0.95rem;
  opacity: 0.9;
}
.logo-svg { width: 22px; height: 22px; stroke: var(--text-primary); }

.main-area {
  flex: 1;
  position: relative;
  width: 100%;
  display: flex;
  flex-direction: column;
}

.welcome-container {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
  padding: 0 40px;
  max-width: 900px;
  margin: 0 auto;
  right: 0;
}

.gradient-title {
  font-size: 3.5rem;
  font-weight: 600;
  margin-bottom: 10px;
  letter-spacing: -1.5px;
  background: linear-gradient(120deg, #ffffff 0%, #888888 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle-text {
  font-size: 1.5rem;
  font-weight: 300;
  color: #666;
}

.chat-messages {
  flex: 1;
  width: 100%;
  overflow-y: auto;
  padding: 20px 0;
  display: flex;
  flex-direction: column;
}

.messages-inner {
  width: 100%;
  max-width: 900px;
  margin: 0 auto;
  padding: 0 40px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding-bottom: 20px;
}

.message {
  max-width: 80%;
  padding: 18px 24px;
  border-radius: 16px;
  font-size: 1rem;
  line-height: 1.6;
  font-weight: 300;
  position: relative;
}

.message.bot {
  align-self: flex-start;
  background-color: var(--msg-bot-bg);
  color: #ddd;
  border: 1px solid rgba(255,255,255,0.05);
  border-bottom-left-radius: 4px;
}

.message.user {
  align-self: flex-end;
  background-color: var(--msg-user-bg);
  color: #fff;
  border-bottom-right-radius: 4px;
}

/* --- FOOTER --- */
.footer-area {
  width: 100%;
  padding: 20px 40px 40px 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  background: linear-gradient(to top, var(--bg-color) 20%, transparent 100%);
  flex-shrink: 0;
  z-index: 20;
}

.footer-content { width: 100%; max-width: 900px; }

.status-indicator {
  height: 24px; margin-bottom: 10px; font-size: 0.8rem; color: var(--accent-color);
  display: flex; align-items: center; gap: 8px; font-weight: 500;
  padding-left: 10px;
}
@keyframes pulse { 0%, 100% { opacity: 0.5; } 50% { opacity: 1; } }
.sparkle { animation: pulse 1.5s infinite; }

.input-wrapper {
  background-color: var(--input-bg);
  border: 1px solid var(--input-border);
  backdrop-filter: blur(12px);
  border-radius: 16px;
  padding: 6px 6px 6px 24px;
  display: flex; align-items: center;
  transition: all 0.3s ease;
  box-shadow: 0 4px 30px rgba(0,0,0,0.3);
}

.input-wrapper.focused, 
.input-wrapper:focus-within {
  border-color: rgba(79, 70, 229, 0.4);
  box-shadow: 0 0 25px rgba(79, 70, 229, 0.15);
}

.input-wrapper input {
  flex: 1; background: transparent; border: none; outline: none;
  font-size: 1rem; color: #fff; padding: 12px 0; font-weight: 300;
}
.input-wrapper input::placeholder { color: #555; }

/* Button */
.send-btn {
  background-color: var(--accent-color);
  border: none; width: 48px; height: 48px; border-radius: 12px;
  cursor: pointer; display: flex; justify-content: center; align-items: center;
  transition: all 0.2s; margin-left: 10px;
  box-shadow: 0 0 15px var(--accent-glow);
}
.send-btn:hover { background-color: #6366f1; transform: translateY(-1px); }
.send-btn:active { transform: scale(0.95); }
.send-icon { stroke: white; width: 20px; height: 20px; }

.fade-up-enter-active, .fade-up-leave-active { transition: all 0.4s ease; }
.fade-up-enter-from, .fade-up-leave-to { opacity: 0; transform: translateY(-20px); }

.fade-in-enter-active { transition: opacity 0.6s ease; }
.fade-in-enter-from { opacity: 0; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

@media (max-width: 600px) {
  .chat-header, .welcome-container, .messages-inner, .footer-area { padding-left: 20px; padding-right: 20px; }
  .gradient-title { font-size: 2.5rem; }
  .subtitle-text { font-size: 1.2rem; }
}
</style>
