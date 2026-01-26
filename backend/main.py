import spacy
import pandas as pd
from fuzzywuzzy import fuzz
from Levenshtein import distance
import numpy as np
import pyphen
import os


try:
    nlp = spacy.load("it_core_news_lg")
except:
    nlp = spacy.load("it_core_news_md")

dic = pyphen.Pyphen(lang='it_IT')


def carica_training_set():
    """Carica esempi predefiniti per guidare l'algoritmo."""
    if os.path.exists('training_set.csv'):
        return pd.read_csv('training_set.csv')
    return pd.DataFrame(columns=['Originale', 'Tema', 'Risultato', 'Tipo'])

def verifica_training_set(base, tema, training_df):
    """Controlla se esiste un match perfetto nel training set."""
    match = training_df[(training_df['Originale'].str.lower() == base.lower()) & 
                        (training_df['Tema'].str.lower() == tema.lower())]
    if not match.empty:
        return match.iloc[0]['Risultato'].upper()
    return None


def fusione_perfetta(base, tema):
    base = base.lower()
    tema = tema.lower()
    
    for i in range(min(len(tema), len(base)), 1, -1):
        if tema.endswith(base[:i]):
            return (tema + base[i:]).upper()
        if base.endswith(tema[:i]):
            return (base + tema[i:]).upper()

    # SILLABIZZAZIONE
    s_base = dic.inserted(base).split('-')
    s_tema = dic.inserted(tema).split('-')
    
    best_dist = 99
    incastro = (0, 0)
    for i, sil_b in enumerate(s_base):
        for j, sil_t in enumerate(s_tema):
            dist = distance(sil_b, sil_t)
            if dist < best_dist:
                best_dist = dist
                incastro = (i, j)
    
    idx_b, idx_t = incastro
    # Ricostruzione: Parte del tema + sillaba d'incastro + resto della base
    risultato = "".join(s_tema[:idx_t]) + s_tema[idx_t] + "".join(s_base[idx_b+1:])
    
    if len(risultato) < len(base):
        risultato = tema[:len(tema)//2] + base[len(base)//3:]
        
    return risultato.upper()



def genera_gioco(prompt):
    if not os.path.exists('nomi.csv'):
        return "Errore: 'nomi.csv' non trovato."
    
    df_nomi = pd.read_csv('nomi.csv')
    training_df = carica_training_set()
    
    parti = prompt.split(maxsplit=1)
    if len(parti) < 2: return "Uso: Categoria Tema"
    
    cat_input, tema_input = parti[0], parti[1]
    
    candidati = df_nomi[df_nomi['Categoria'].str.contains(cat_input, case=False, na=False)]['Nome'].tolist()
    if not candidati: return "Categoria non trovata."


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
                risultato_ts = verifica_training_set(pezzo, t, training_df)
                
                if risultato_ts:
                    score = 200 
                    gioco_parola = risultato_ts
                else:
                    score = fuzz.ratio(pezzo.lower(), t.lower())
                    if t[-2:] == pezzo[:2]: score += 30 
                    gioco_parola = fusione_perfetta(pezzo, t)

                if score > max_score:
                    max_score = score
                    nuovo_nome = list(parti_nome)
                    nuovo_nome[i] = gioco_parola
                    best_match = {
                        'output': " ".join(nuovo_nome),
                        'orig': nome,
                        'info': f"'{t}' + '{pezzo}'"
                    }

    if not best_match: return "Nessun incastro trovato."
    return f"\n🎭 GIOCO: {best_match['output']}\n(Da: {best_match['orig']} | Info: {best_match['info']})"

if __name__ == "__main__":
    print("--- GENERATORE V6 (Sillabico + Training Set) ---")
    while True:
        p = input("\nInserisci Categoria e Tema: ")
        if p.lower() == 'exit': break
        print(genera_gioco(p))