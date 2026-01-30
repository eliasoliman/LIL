<template>
  <div class="app-layout">
    
    <header class="header">
      <span class="logo">LEXIS</span>
    </header>

    <main class="main-area" ref="scrollContainer">
      
      <div v-if="messages.length === 0" class="hero-container">
        <h1 class="hero-title">Ciao, Sono Lexis</h1>
        <p class="hero-subtitle">Che gioco di parole posso creare per te?</p>
      </div>

      <div v-else class="chat-container">
        
        <div v-for="(msg, index) in messages" :key="index" class="message-row" :class="msg.sender">
          
          <div v-if="msg.sender === 'user'" class="bubble user-bubble">
            {{ msg.text }}
          </div>

          <div v-else class="result-card">
            <span class="card-label">RISULTATO</span>
            <h2 class="card-output">{{ msg.output }}</h2>
            <div class="card-details">
              <p><strong>Da:</strong> {{ msg.originale }}</p>
              <p><strong>Info:</strong> {{ msg.info }}</p>
            </div>
          </div>

        </div>

        <div v-if="loading" class="message-row ai">
          <div class="result-card loading-card">
            <div class="loading-dots">
              <span class="dot"></span><span class="dot"></span><span class="dot"></span>
            </div>
          </div>
        </div>

      </div>
    </main>

    <footer class="footer">
      <div class="input-box">
        <input 
          v-model="inputText"
          type="text"
          placeholder="Dimmi una Categoria e un Tema"
          @keyup.enter="sendMessage"
          class="text-input"
          :disabled="loading"
        />
        <button 
          @click="sendMessage"
          :disabled="!inputText.trim() || loading"
          class="send-btn"
        >
          <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">
            <line x1="12" y1="19" x2="12" y2="5"></line>
            <polyline points="5 12 12 5 19 12"></polyline>
          </svg>
        </button>
      </div>
    </footer>

  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import axios from 'axios'

const inputText = ref('')
const messages = ref([])
const loading = ref(false)
const scrollContainer = ref(null)

const scrollToBottom = async () => {
  await nextTick()
  if (scrollContainer.value) {
    scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight
  }
}

const sendMessage = async () => {
  if (!inputText.value.trim() || loading.value) return

  // 1. Aggiungi messaggio Utente
  const userText = inputText.value
  messages.value.push({ text: userText, sender: 'user' })
  inputText.value = ''
  loading.value = true
  scrollToBottom()

  try {
    // 2. Chiama il Backend
    const response = await axios.post(`${getApiUrl()}/genera`, {
      prompt: userText
    })

    // 3. Aggiungi la CARD dell'AI
    messages.value.push({ 
      sender: 'ai',
      originale: response.data.originale,
      output: response.data.output,
      info: response.data.info
    })

  } catch (error) {
    // Fallback errore
    messages.value.push({ 
      sender: 'ai',
      originale: "Errore",
      output: "Server non raggiungibile",
      info: "Controlla che main.py sia attivo"
    })
  } finally {
    loading.value = false
    scrollToBottom()
  }
}
</script>

<style scoped>
/* STRUTTURA GENERALE */
.app-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #111111;
  color: white;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

.header { height: 60px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.logo { font-weight: 700; letter-spacing: 1px; font-size: 14px; color: #fff; }

.main-area {
  flex: 1;
  position: relative;
  overflow-y: auto;
  padding: 0 20px;
  display: flex;
  flex-direction: column;
}

/* HERO SECTION (Allineata a Sinistra) */
.hero-container {
  margin: auto;
  margin-left: auto; margin-right: auto;
  width: 100%; max-width: 720px;
  text-align: left;
}
.hero-title { font-size: 32px; font-weight: 700; margin-bottom: 10px; }
.hero-subtitle { font-size: 18px; color: #888; font-weight: 400; }

/* CHAT CONTAINER */
.chat-container {
  width: 100%;
  max-width: 720px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 30px; /* Più spazio tra i messaggi per ospitare le card */
  padding-bottom: 20px;
}

.message-row { display: flex; width: 100%; }
.message-row.user { justify-content: flex-end; }
.message-row.ai { justify-content: flex-start; }

/* BOLLA UTENTE (Semplice) */
.user-bubble {
  background-color: #5856D6;
  color: white;
  padding: 12px 18px;
  border-radius: 18px;
  border-bottom-right-radius: 4px;
  max-width: 80%;
  font-size: 16px;
}

/* --- CARD STYLE (Per l'AI) --- */
.result-card {
  background: #1a1a1a;
  padding: 30px;
  border-radius: 20px;
  border-bottom-left-radius: 4px;
  border: 1px solid #333;
  width: 100%; /* Occupa tutta la larghezza disponibile (fino a 720px) */
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
  animation: slideIn 0.3s ease-out;
}

.card-label {
  font-size: 10px;
  letter-spacing: 1.5px;
  color: #5856D6;
  font-weight: bold;
  text-transform: uppercase;
  display: block;
  margin-bottom: 10px;
}

.card-output {
  font-size: 32px;
  margin: 10px 0 20px 0;
  color: #fff;
  font-weight: 600;
  line-height: 1.2;
}

.card-details {
  border-top: 1px solid #333;
  padding-top: 15px;
  color: #888;
  font-size: 14px;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.card-details strong { color: #ccc; }

/* INPUT BAR */
.footer { padding: 20px; padding-bottom: 40px; display: flex; justify-content: center; background-color: #111111; flex-shrink: 0; }
.input-box { position: relative; width: 100%; max-width: 720px; }
.text-input { width: 100%; background-color: #1F1F1F; border: 1px solid #333; border-radius: 24px; padding: 16px 20px; padding-right: 50px; color: white; font-size: 16px; outline: none; transition: border-color 0.2s; }
.text-input:focus { border-color: #555; }
.send-btn { position: absolute; right: 8px; top: 50%; transform: translateY(-50%); background-color: #5856D6; color: white; border: none; width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; }
.send-btn:disabled { background-color: #333; color: #555; cursor: not-allowed; }

/* LOADING ANIMATION */
.loading-card { display: flex; align-items: center; justify-content: center; min-height: 100px; }
.dot { width: 8px; height: 8px; background-color: #555; border-radius: 50%; margin: 0 4px; animation: bounce 1.4s infinite ease-in-out both; }
.dot:nth-child(1) { animation-delay: -0.32s; }
.dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }
@keyframes slideIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>