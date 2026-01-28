from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import spacy
import pandas as pd
from fuzzywuzzy import fuzz
from Levenshtein import distance
import numpy as np
import pyphen
import os
import uvicorn

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PATH_CSV = os.path.join(BASE_DIR, 'nomi.csv')

# Configurazione CORS per permettere richieste da qualsiasi origine
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Caricamento del modello linguistico italiano e del dizionario di sillabazione
try:

    nlp = spacy.load("it_core_news_lg")

except:

    nlp = spacy.load("it_core_news_md")
dic = pyphen.Pyphen(lang='it_IT')

class GiocoRequest(BaseModel):
    prompt: str

def fusione(base, tema):
    """
    Funzione che implementa la fusione linguistica tra due parole.
    
    Strategia a tre livelli:
    1. Cerca sovrapposizioni tra suffisso e prefisso delle parole
    2. Se non trova sovrapposizioni, analizza le sillabe e cerca quelle più simili
    3. Sostituisce la sillaba più simile della parola base con quella del tema
    
    Restituisce una parola composta in maiuscolo.
    """
    base, tema = base.lower(), tema.lower()
    
    # Primo tentativo: ricerca sovrapposizioni tra le estremità delle parole
    for i in range(min(len(tema), len(base)), 1, -1):
        if tema.endswith(base[:i]): return (tema + base[i:]).upper()
        if base.endswith(tema[:i]): return (base + tema[i:]).upper()

    # Secondo tentativo: analisi basata su sillabe
    s_base = dic.inserted(base).split('-')
    s_tema = dic.inserted(tema).split('-')
    
    # Ricerca delle sillabe più simili tra le due parole usando distanza di Levenshtein
    best_dist, incastro = 99, (0, 0)
    for i, sil_b in enumerate(s_base):
        for j, sil_t in enumerate(s_tema):
            dist = distance(sil_b, sil_t)
            if dist < best_dist:
                best_dist, incastro = dist, (i, j)
    
    # Costruzione della parola finale sostituendo la sillaba della base con quella del tema
    idx_b, idx_t = incastro
    risultato = "".join(s_tema[:idx_t]) + s_tema[idx_t] + "".join(s_base[idx_b+1:])
    
    # Fallback: se il risultato è troppo corto, concatena porzioni delle due parole
    if len(risultato) < len(base):
        risultato = tema[:len(tema)//2] + base[len(base)//3:]
    
    return risultato.upper()

@app.post("/genera")
async def genera(req: GiocoRequest):
    """
    Endpoint principale che genera giochi di parole.
    
    Processo:
    1. Estrae categoria e tema dal prompt dell'utente
    2. Filtra i nomi nel CSV in base alla categoria
    3. Espande il tema usando similarità semantica tramite word embeddings
    4. Per ogni nome candidato, cerca corrispondenze con i temi correlati
    5. Calcola uno score di similarità e genera la fusione migliore
    6. Restituisce il risultato con score più alto
    """
    if not os.path.exists(PATH_CSV):
        raise HTTPException(status_code=404, detail=f"File non trovato in: {PATH_CSV}")
    
    df_nomi = pd.read_csv(PATH_CSV)
    parti = req.prompt.split(maxsplit=1)
    if len(parti) < 2: return {"errore": "Formato richiesto: Categoria Tema"}
    
    cat_input, tema_input = parti[0], parti[1]
    
    # Filtraggio dei nomi in base alla categoria specificata
    candidati = df_nomi[df_nomi['Categoria'].str.contains(cat_input, case=False, na=False)]['Nome'].tolist()
    
    if not candidati: return {"errore": "Categoria non trovata"}

    # Espansione semantica del tema usando word embeddings di spaCy
    doc = nlp(tema_input.lower())
    temi_correlati = [doc[0].lemma_]
    
    # Ricerca di parole semanticamente simili al tema
    if doc[0].has_vector:
        simili = nlp.vocab.vectors.most_similar(np.asarray([doc[0].vector]), n=6)
        for key in simili[0][0]:
            parola = nlp.vocab.strings[key].lower()
            # Filtra parole alfabetiche e sufficientemente diverse dal tema originale
            if parola.isalpha() and distance(parola, tema_input) > 3:
                temi_correlati.append(nlp(parola)[0].lemma_)

    # Ricerca del miglior abbinamento tra nomi candidati e temi correlati
    best_match = None
    max_score = -1

    for nome in candidati:
        parti_nome = nome.split()
        for i, pezzo in enumerate(parti_nome):
            if len(pezzo) < 4: continue  # Ignora parole troppo corte
            
            for t in temi_correlati:
                # Calcolo dello score di similarità con fuzzywuzzy
                score = fuzz.ratio(pezzo.lower(), t.lower())
                
                # Bonus se c'è una sovrapposizione parziale tra suffisso del tema e prefisso del pezzo
                if t[-2:] == pezzo[:2]: score += 30 
                
                gioco_parola = fusione(pezzo, t)

                # Aggiornamento del miglior risultato
                if score > max_score:
                    max_score = score
                    nuovo_nome = list(parti_nome)
                    nuovo_nome[i] = gioco_parola
                    best_match = {
                        "output": " ".join(nuovo_nome),
                        "originale": nome,
                        "info": f"'{t}' + '{pezzo}'"
                    }

    return best_match if best_match else {"errore": "Nessun incastro trovato"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)