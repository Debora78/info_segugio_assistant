# inizializzare il sistema
# importa la libreria Chainlit con nome abbreviato 'cl'
import chainlit as cl

import json # libreria json permette di lavorare con i file in formato JSON, che è un formato di scambio dati molto comune

# importa la libreria OpenAI per interagire con il modello di intelligenza artificiale
from openai import OpenAI

#importa dal file config la classe Config che contiene le configurazioni necessarie per l'API
from config import Config

from tavily import TavilyClient # importa TavilyClient per le ricerche web

from prompts import query_writer_instructions # importa le istruzioni per il generatore di query dal file prompts.py

#inizializzazione del Client OpenAI con le configurazioni 
client = OpenAI(base_url = Config.AI_API_URL, api_key = Config.AI_API_KEY)

# Funzione per interagire con il modello di intelligenza artificiale
# Questa funzione si chiama 'llm' e prende in input il
# developer_prompt che è la parte in cui si definisce il comportamento del modello, mentre user_prompt è il messaggio dell'utente a cui il modello deve rispondere
# La temperatura controlla la casualità delle risposte generate, posizionata su 0 che indica al modello di non inventare nulla, mentre il formato di risposta specifica come deve essere strutturata la risposta(output strutturato)
# I primi 2 parametri sono obbligatori, mentre gli altri due sono opzionali e hanno dei valori di default(0)
def llm(developer_prompt, user_prompt, temperature = 0, response_format = {"type": "json_object"}):

    response = client.chat.completions.create(
        model=Config.LLM_MODEL_LOW,  # Utilizza il modello specificato nella configurazione
        messages=[
            {"role": "developer", "content": developer_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature = temperature,
        response_format = response_format
    )
    return response.choices[0].message.content # si sceglie la prima risposta generata dal modello e restituisce il contenuto del messaggio


#Genera una query ottimizzata per la ricerca web
def optimize_search_query(research_topic):
    formatted_instructions = query_writer_instructions.format(research_topic = research_topic)
    result = llm(formatted_instructions, "Genera una query per la ricerca web:")
    obj = json.loads(result)  # Converte la stringa JSON in un dizionario Python
    # print(obj)  # Stampa l'oggetto
    return obj

# Funzione per formattare il contenuto dei risultati della ricerca
# Questa funzione prende in input un risultato della ricerca e restituisce una stringa formattata con il titolo, l'URL e il contenuto più rilevante
def _format_content(result):
    return f"""
Fonte {result['title']}:\n===\n
URL:{result['url']}\n===\n
Contenuto più rilevante: {result['content']}\n===\n
"""

def web_research(search_query):
    # tavily_client = TavilyClient(api_key="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")  # Inizializza il client Tavily con la tua chiave API
    # # Esegui una query di ricerca semplice
    # response = tavily_client.search(search_query)
    # # Accedi ai risultati della ricerca
    # print(response)
    # MIGLIORAMENTO DEL CODICE
    tavily_api_key = "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"  # La tua chiave API Tavily
    max_results = 1  # Numero massimo di risultati da raccogliere
    include_raw = False # Indica se includere i risultati grezzi
    
    client = TavilyClient(api_key = tavily_api_key)  # Inizializza il client Tavily con la tua chiave API
    response = client.search(
        query=search_query,  # La query di ricerca da eseguire
        max_results=max_results,  # Numero massimo di risultati da raccogliere
        include_raw_content=include_raw  # Include i risultati grezzi
        )
    results = response.get('results', [])  # Ottieni i risultati dalla risposta(se non ci sono risultati, restituisce una lista vuota)
    titles = [result['title'] for result in results]  # Estrai i titoli dei risultati (list comprehension)
    contents = [_format_content(result) for result in results]  # Estrai i contenuti dei risultati (list comprehension)
    #print(response)  # Stampa la risposta della ricerca
    #print(title, contents)  # Stampa i titoli e i contenuti dei risultati
    return {
        "sources_gathered": titles,  # Lista dei titoli dei risultati della ricerca
        "web_research_results": contents  # Lista dei contenuti formattati dei risultati della ricerca
    }

# con questo decoratore diciamo che ogni volta che viene ricevuto un messaggio dall'interfaccia, viene chiamata la funzione main
# in message metti le informazioni che l'utente ha scritto
@cl.on_message
async def main(message: cl.Message):
    # Fase 1: Generazione della query iniziale
    user_message = message.content
    osq = optimize_search_query(user_message)
    
    
    # feedback per l'utente
    # catturo la query ottimizzata, l'aspetto su cui si è concentrato e il motivo della scelta
    # osq è un dizionario che contiene le chiavi 'query', 'aspect' e 'reason'
    query, aspect, reason = osq['query'], osq['aspect'], osq['reason']
    # Invia un messaggio all'utente con la query ottimizzata, l'aspetto e il motivo
    await cl.Message(
        author="system_assistant", 
        content=f"Query di ricerca ottimizzata:\n {query}.\n Mi sonosoffermato su questo aspetto:\n {aspect}. \n Per questo motivo:\n {reason}.\n"
         ).send()
    
    # Esegui la ricerca web 
    results = web_research(query)

    #feedback per l'utente
    #[sources_gathered][0] si riferisce alla prima pagina trovata nella ricerca
    await cl.Message(
        author="system_assistant",
        content=f"Fonti trovate: {result['sources_gathered'][0]}"
        ).send()

    summary = llm("Sei un assistente molto in gamba e sai riassumere molto bene le informazioni.",
                  f"Ecco le informzioni che devi riassumere: {results['web_research_results']}",
                  temperature=0.2, None
                  ) # None indica che voglio un testo normale e non un JSON che è il formato di default
    
    # feedback per l'utente
    await cl.Message(
        author="system_assistant",
        content=f"Riassunto attuale: {summary}"
        ).send()