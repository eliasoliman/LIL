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

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    nlp = spacy.load("it_core_news_lg")
except:
    nlp = spacy.load("it_core_news_md")

dic = pyphen.Pyphen(lang='it_IT')

class GiocoRequest(BaseModel):
    prompt: str

def fusione_perfetta(base, tema):
    base, tema = base.lower(), tema.lower()
    for i in range(min(len(tema), len(base)), 1, -1):
        if tema.endswith(base[:i]): return (tema + base[i:]).upper()
        if base.endswith(tema[:i]): return (base + tema[i:]).upper()

    s_base = dic.inserted(base).split('-')
    s_tema = dic.inserted(tema).split('-')
    
    best_dist, incastro = 99, (0, 0)
    for i, sil_b in enumerate(s_base):
        for j, sil_t in enumerate(s_tema):
            dist = distance(sil_b, sil_t)
            if dist < best_dist:
                best_dist, incastro = dist, (i, j)
    
    idx_b, idx_t = incastro
    risultato = "".join(s_tema[:idx_t]) + s_tema[idx_t] + "".join(s_base[idx_b+1:])
    if len(risultato) < len(base):
        risultato = tema[:len(tema)//2] + base[len(base)//3:]
    return risultato.upper()

@app.post("/genera")
async def genera(req: GiocoRequest):
    if not os.path.exists('nomi.csv'):
        raise HTTPException(status_code=404, detail="File nomi.csv non trovato")
    
    df_nomi = pd.read_csv('nomi.csv')
    parti = req.prompt.split(maxsplit=1)
    if len(parti) < 2: return {"errore": "Formato richiesto: Categoria Tema"}
    
    cat_input, tema_input = parti[0], parti[1]
    candidati = df_nomi[df_nomi['Categoria'].str.contains(cat_input, case=False, na=False)]['Nome'].tolist()
    
    if not candidati: return {"errore": "Categoria non trovata"}

    doc = nlp(tema_input.lower())
    temi_correlati = [doc[0].lemma_]
    if doc[0].has_vector:
        simili = nlp.vocab.vectors.most_similar(np.asarray([doc[0].vector]), n=6)
        for key in simili[0][0]:
            parola = nlp.vocab.strings[key].lower()
            if parola.isalpha() and distance(parola, tema_input) > 3:
                temi_correlati.append(nlp(parola)[0].lemma_)

    best_match = None
    max_score = -1

    for nome in candidati:
        parti_nome = nome.split()
        for i, pezzo in enumerate(parti_nome):
            if len(pezzo) < 4: continue
            for t in temi_correlati:
                score = fuzz.ratio(pezzo.lower(), t.lower())
                if t[-2:] == pezzo[:2]: score += 30 
                gioco_parola = fusione_perfetta(pezzo, t)

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