<script setup>
import { ref, nextTick, watch } from 'vue';

// --- STATO ---
const userInput = ref('');
const messages = ref([]);
const isChatActive = ref(false);
const chatContainer = ref(null);
const isBotTyping = ref(false);

// --- LOGICA ---

// Funzione per scorrere in basso automaticamente
const scrollToBottom = async () => {
  await nextTick();
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
  }
};

// Osserva i messaggi e scrolla quando cambiano
watch(messages, () => {
  scrollToBottom();
}, { deep: true });

// Gestione invio messaggio
const handleSend = () => {
  const text = userInput.value.trim();
  if (!text) return;

  // 1. Attiva interfaccia chat se è il primo messaggio
  if (!isChatActive.value) {
    isChatActive.value = true;
  }

  // 2. Aggiungi messaggio utente
  messages.value.push({
    id: Date.now(),
    text: text,
    sender: 'user'
  });

  userInput.value = ''; // Pulisci input
  isBotTyping.value = true;

  // 3. Simula risposta Bot
  setTimeout(() => {
    const risposte = [
      "Sto elaborando i dati richiesti...",
      "Ho trovato una corrispondenza nei miei archivi.",
      "Certamente. Ecco cosa posso dirti a riguardo.",
      "Interessante punto di vista. Analizziamolo."
    ];
    const randomResp = risposte[Math.floor(Math.random() * risposte.length)];
    
    messages.value.push({
      id: Date.now() + 1,
      text: randomResp,
      sender: 'bot'
    });
    
    isBotTyping.value = false;
  }, 1000);
};
</script>

<template>
  <v-app class="lexis-app">
    
    <v-app-bar flat height="80" class="chat-header">
      <div class="brand">Lexis</div>
    </v-app-bar>

    <v-main class="main-area">
      <v-container class="fill-height d-flex flex-column justify-center align-center position-relative">
        
        <transition name="fade">
          <div v-if="!isChatActive" class="welcome-container text-center">
            <h1>Ciao, Sono Lexis</h1>
            <h2>Che gioco di parole posso creare per te?</h2>
          </div>
        </transition>

        <transition name="fade">
          <div 
            v-show="isChatActive" 
            ref="chatContainer"
            class="chat-messages"
          >
            <div class="messages-container">
              <div 
                v-for="msg in messages" 
                :key="msg.id" 
                :class="['message', msg.sender]"
              >
                {{ msg.text }}
              </div>
              
              <div v-if="isBotTyping" class="message bot typing">
                ...
              </div>
            </div>
          </div>
        </transition>

      </v-container>
    </v-main>

    <v-footer app height="100" class="footer-area">
      <div class="input-wrapper">
        <input 
          v-model="userInput" 
          type="text" 
          placeholder="Dimmi un Tema e una Categoria..." 
          @keypress.enter="handleSend"
          autocomplete="off"
        >
        <button @click="handleSend" class="send-btn">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="5" y1="12" x2="19" y2="12"></line>
            <polyline points="12 5 19 12 12 19"></polyline>
          </svg>
        </button>
      </div>
    </v-footer>
  </v-app>
</template>

<style scoped>
/* --- STILI OVERRIDE/CUSTOM --- */
/* Manteniamo i colori originali sovrascrivendo i default di Vuetify dove serve */

.lexis-app {
  background-color: #141416 !important;
  color: #F3F4F6;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

/* HEADER */
.chat-header {
  background-color: #141416 !important;
  border-bottom: 1px solid #262629;
  display: flex;
  justify-content: center;
}

/* Per centrare il titolo nell'app bar di Vuetify */
:deep(.v-toolbar__content) {
  justify-content: center;
}

.brand {
  font-weight: 600;
  font-size: 1.2rem;
  color: #F3F4F6;
}

/* WELCOME SCREEN */
.welcome-container h1 {
  color: #F3F4F6;
  margin-bottom: 0.5rem;
}

.welcome-container h2 {
  font-size: 1.5rem;
  font-weight: 400;
  color: #9CA3AF;
}

/* CHAT AREA */
.chat-messages {
  width: 100%;
  max-width: 900px;
  height: 100%;
  overflow-y: auto;
  padding: 20px 0;
  /* Nascondi scrollbar nativa per estetica */
  scrollbar-width: thin;
  scrollbar-color: #363639 #141416;
}

.messages-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding-bottom: 20px;
}

.message {
  max-width: 80%;
  padding: 15px 25px;
  border-radius: 20px;
  font-size: 1rem;
  line-height: 1.5;
  animation: popIn 0.3s ease forwards;
}

@keyframes popIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.message.bot {
  align-self: flex-start;
  background-color: #262629;
  color: #E5E7EB;
  border: 1px solid #363639;
}

.message.user {
  align-self: flex-end;
  background-color: #4f46e5;
  color: #FFFFFF;
}

/* FOOTER & INPUT */
.footer-area {
  background-color: #141416 !important;
  display: flex;
  justify-content: center;
  align-items: flex-start; /* Allinea in alto nel footer */
  padding-top: 20px;
}

.input-wrapper {
  width: 100%;
  max-width: 900px;
  background-color: #1c1c1f;
  border: 1px solid #363639;
  border-radius: 50px;
  padding: 8px 10px 8px 25px;
  display: flex;
  align-items: center;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}

.input-wrapper input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  font-size: 1rem;
  color: #F3F4F6;
  padding: 10px 0;
}

.input-wrapper input::placeholder {
  color: #6B7280;
}

.send-btn {
  background-color: #4f46e5;
  border: none;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  color: white;
  transition: background-color 0.2s;
  margin-left: 10px;
}

.send-btn:hover {
  background-color: #4338ca;
}

/* Transizioni Vue */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.4s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>