<template>
  <div class="app-container">
    <header class="header">
      <span class="logo">LEXIS</span>
    </header>

    <main class="main-content">
      
      <div v-if="!risultato && !loading" class="hero-section">
        <h1 class="title">Ciao, Sono Lexis</h1>
        <p class="subtitle">Che gioco di parole posso creare per te?</p>
      </div>

      <div v-if="risultato" class="result-container">
        <div class="result-card">
          <span class="result-label">RISULTATO</span>
          <h2 class="result-output">{{ risultato.output }}</h2>
          <div class="result-details">
            <p><strong>Da:</strong> {{ risultato.originale }}</p>
            <p><strong>Mix:</strong> {{ risultato.info }}</p>
          </div>
        </div>
        <button @click="risultato = null" class="btn-reset">Crea un altro gioco</button>
      </div>

      <div v-if="loading" class="loader-container">
        <div class="spinner"></div>
      </div>
    </main>

    <footer class="footer">
      <div class="input-wrapper">
        <input 
          v-model="query"
          type="text"
          placeholder="Dimmi un Tema e una Categoria..."
          @keyup.enter="inviaRichiesta"
          class="custom-input"
        />
        <button 
          @click="inviaRichiesta"
          :disabled="!query || loading"
          class="send-button"
        >
          <svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none">
            <line x1="12" y1="19" x2="12" y2="5"></line>
            <polyline points="5 12 12 5 19 12"></polyline>
          </svg>
        </button>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const query = ref('')
const risultato = ref(null)
const loading = ref(false)

const inviaRichiesta = async () => {
  if (!query.value || loading.value) return
  loading.value = true
  try {
    const response = await axios.post('http://127.0.0.1:8000/genera', {
      prompt: query.value
    })
    risultato.value = response.data
    query.value = ''
  } catch (err) {
    alert("Errore di connessione al server.");
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* Reset base */
:global(body) {
  margin: 0;
  padding: 0;
  background-color: #111111; /* Sfondo scuro come immagine */
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  color: #ffffff;
}

.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.header {
  padding: 20px;
  display: flex;
  justify-content: center;
}

.logo {
  font-size: 14px;
  letter-spacing: 2px;
  color: #888;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0 20px;
  margin-top: -100px; /* Alza il testo verso il centro alto */
}

.hero-section {
  width: 100%;
  max-width: 650px;
}

.title {
  font-size: 42px;
  font-weight: 600;
  margin: 0 0 10px 0;
}

.subtitle {
  font-size: 20px;
  color: #888;
  font-weight: 300;
  margin: 0;
}

/* Container Risultato */
.result-container {
  width: 100%;
  max-width: 650px;
  animation: slideUp 0.4s ease-out;
}

.result-card {
  background: #1a1a1a;
  padding: 40px;
  border-radius: 24px;
  border: 1px solid #333;
}

.result-label {
  font-size: 10px;
  letter-spacing: 1px;
  color: #6366f1;
  font-weight: bold;
}

.result-output {
  font-size: 48px;
  margin: 15px 0;
  color: #fff;
}

.result-details {
  border-top: 1px solid #333;
  padding-top: 20px;
  color: #666;
  font-size: 14px;
}

.btn-reset {
  background: none;
  border: none;
  color: #555;
  margin-top: 20px;
  cursor: pointer;
  font-size: 14px;
}

.btn-reset:hover { color: #fff; }

/* Barra di Input */
.footer {
  padding: 40px 20px;
  display: flex;
  justify-content: center;
}

.input-wrapper {
  position: relative;
  width: 100%;
  max-width: 768px;
}

.custom-input {
  width: 100%;
  background-color: #222222;
  border: 1px solid #333;
  border-radius: 18px;
  padding: 18px 25px;
  padding-right: 60px;
  color: white;
  font-size: 16px;
  box-sizing: border-box;
  transition: border 0.3s;
}

.custom-input:focus {
  outline: none;
  border-color: #444;
}

.send-button {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background-color: #6366f1; /* Colore viola/blu della freccia */
  border: none;
  border-radius: 12px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  cursor: pointer;
  transition: opacity 0.2s;
}

.send-button:disabled {
  background-color: #333;
  color: #555;
  cursor: not-allowed;
}

/* Spinner */
.spinner {
  width: 30px;
  height: 30px;
  border: 3px solid #333;
  border-top: 3px solid #6366f1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }
@keyframes slideUp { 
  from { opacity: 0; transform: translateY(20px); } 
  to { opacity: 1; transform: translateY(0); } 
}
</style>