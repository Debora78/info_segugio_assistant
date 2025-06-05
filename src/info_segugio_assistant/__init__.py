# inizializzare il sistema

# importa la libreria Chainlit con nome  abbreviato 'cl'
import chainlit as cl

import os
from dotenv import load_dotenv

# Carica le variabili d'ambiente dal file .env
load_dotenv()

# Recupera le chiavi dalle variabili d'ambiente
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
OPENAI_API_URL = os.getenv("OPENAI_API_URL") # Recupera anche l'URL se presente nel .env

#  Verifica che le chiavi siano state caricate
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY non trovata. Assicurati che sia nel file .env")
if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY non trovata. Assicurati che sia nel file .env")

import json # libreria json permette di lavorare con i file in formato JSON, che è un formato di scambio dati molto comune

# importa la libreria OpenAI per interagire con il modello di intelligenza artificiale
from openai import OpenAI

#importa dal file config la classe Config che contiene le configurazioni necessarie per l'API
#from config import Config(commentata perchè non è più necessaria, ora le chiavi sono caricate dalle variabili d'ambiente ne file .env)

from tavily import TavilyClient # importa TavilyClient per le ricerche web

from prompts import query_writer_instructions, summarizer_instructions, reflection_instructions # importa le istruzioni per il generatore di query, per il riassunto e per la riflessione dal file prompts.py

#inizializzazione del Client OpenAI con le configurazioni 
client = OpenAI(base_url = OPENAI_API_URL, api_key = OPENAI_API_KEY)

# Funzione per interagire con il modello di intelligenza artificiale
# Questa funzione si chiama 'llm' e prende in input il
# developer_prompt che è la parte in cui si definisce il comportamento del modello, mentre user_prompt è il messaggio dell'utente a cui il modello deve rispondere
# La temperatura controlla la casualità delle risposte generate, posizionata su 0 che indica al modello di non inventare nulla, mentre il formato di risposta specifica come deve essere strutturata la risposta(output strutturato)
# I primi 2 parametri sono obbligatori, mentre gli altri due sono opzionali e hanno dei valori di default(0)
def llm(developer_prompt, user_prompt, temperature = 0, response_format = {"type": "json_object"}):

    response = client.chat.completions.create(
        model=LLM_MODEL_LOW,  # Utilizza il modello specificato nella configurazione
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
    #tavily_api_key = "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"  # La tua chiave API Tavily commentata perché ora la chiave API è caricata dalle variabili d'ambiente nel file .env
    max_results = 1  # Numero massimo di risultati da raccogliere
    include_raw = False # Indica se includere i risultati grezzi
    
    client = TavilyClient(api_key = TAVILY_API_KEY) # Ora usa la variabile caricata da .env
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
    
    # Questa funzione sintetizza i risultati della ricerca in un riassunto coerente
    # Prende in input i risultati della ricerca web, il tema della ricerca e un riassunto corrente (se presente)
    #web_research_results è una lista di risultati della ricerca web, research_topic è la query originaria  e running_summary è il riassunto se esistente
def summarize_sources(web_research_results, research_topic, running_summary=None):

    current_results = web_research_results[-1]  # Prende l'ultimo risultato della ricerca web

    if running_summary:
        message = (
            f"Estendi questo riassunto: {running_summary}\n\n"
            f"Con questi nuovi risultati: {current_results}"
            f"Sul tema: {research_topic}"
        )
    else:
        message = (
            f"Genera un riassunto di questi risultati: {current_results}"
                f"Sul tema: {research_topic}"
            )
            
    output_formatter = None  # Indica che vogliamo un testo normale e non un JSON che è il formato di default
    return llm(summarizer_instructions, message, 0.2, output_formatter)  # Chiama la funzione llm con le istruzioni per il riassunto e il messaggio formattato , message è il messaggio dell'utente.

# Questa funzione analizza il riassunto corrente e genera una domanda di approfondimento
# Prende in input l'argomento e il riassunto corrente
def reflect_on_summary(research_topic, running_summary):
    result = llm(
        reflection_instructions.format(research_topic=research_topic),  # Inserisce il tema della ricerca nelle istruzioni
        f"Identifica una lacuna e genera una domanda per la prossima ricerca basandoti su: {running_summary}"
    )  # Passa il riassunto corrente (running_summary) 
    # Converte la risposta in un oggetto JSON
    return json.loads(result)


# con questo decoratore diciamo che ogni volta che viene ricevuto un messaggio dall'interfaccia, viene chiamata la funzione main
# in message metti le informazioni che l'utente ha scritto
@cl.on_message
async def main(message: cl.Message):
    # !FASE 1: Generazione della query iniziale
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
    
    # !FASE 2: Ciclo di ricerca e approfondimento
    running_summary = None  # Inizializza il riassunto corrente come None, qui verrà accumulato in nuovo riassunto
    
    # Creo un contatore per tenere traccia del numero di ricerche effettuate
    # Questo contatore può essere utile per limitare il numero di ricerche o per altre logiche di controllo
    max_cycles = 4  # Numero massimo di cicli di ricerca da effettuare
    # Creo un ciclo infinito per continuare a fare ricerche e aggiornare il riassunto
    # Questo ciclo continuerà fino a quando l'utente non deciderà di interrompere la ricerca
    while True:
    
        # Esegui la ricerca web 
        results = web_research(query)

        #feedback per l'utente
        #[sources_gathered][0] si riferisce alla prima pagina trovata nella ricerca
        await cl.Message(
            author="system_assistant",
            content=f"Fonti trovate: {results['sources_gathered'][0]}"
            ).send()

        # Sostituisco questo codice con una funzione
        # None indica che voglio un testo normale e non un JSON che è il formato di default
        # summary = llm(
        #         "Sei un assistente molto in gamba e sai riassumere molto bene le informazioni.",
        #         f"Ecco le informzioni che devi riassumere: {results['web_research_results']}",
        #         0.2, None
        #         )
        
        # print(f"Ecco le informzioni che devi riassumere: {results['web_research_results']}")
        
        #Genera o aggiorna il riassunto 
        # Ad ogni ciclo il riassunto viene migliorato con le nuove informazioni raccolte dalla ricerca web
        # summarize_sources è il nome della funzione che sintetizza le informazioni dalle fonti raccolte
        # il primo parametro è la lista dei risultati della ricerca, il secondo è la query ottimizzata di ricerca e il terzo è il riassunto corrente fino a quel momento per ottenere un nuovo riassunto (summary)
        summary = summarize_sources(results['web_research_results'],query, running_summary)
        # Devo aggiornare il riassunto corrente con il nuovo riassunto
        running_summary = summary  # Aggiorna il riassunto corrente con il nuovo riassunto generato
        
        # feedback per l'utente
        await cl.Message(
            author="system_assistant",
            content=f"Riassunto attuale: {summary}"
            ).send()
        
        # dal 1° giro al 3° giro del ciclo rifletto, il 4° giro non rifletto più perchè è l'ultimo giro e non ha senso riflettere su un riassunto che non verrà più aggiornato 
        # Se abbiamo finito il numero massimo di cicli, Esci
        max_cycles -= 1  # Decrementa il contatore dei cicli
        if max_cycles <= 0: # Se il contatore dei cicli è minore o uguale a 0, esci dal ciclo
            break
        
        # Genera la prossima query di approfondimento
        # query è la query ottimizzata, summary è il riassunto corrente che passeremo alla funzione reflect_on_summary
        #ros è un dizionario
        ros = reflect_on_summary(query, summary)
        query = ros.get('domanda_approfondimento', f"Dimmi di più su {query}")  # Se non c'è una domanda di approfondimento, usa quella di default( "Dimmi di più su {query}") che è quella originale.
        
        # feedback per l'utente
        await cl.Message(
            author="system_assistant",
            content=f"Prossima ricerca:\n {query}. \n Mi sono soffermato su questo perché:\n {ros.get('lacuna_conoscenza', '')}"  # lacuna_conoscenza è la chiave dell'oggetto ros che contiene le informazioni mancanti, '' è il default se non c'è una lacuna_conoscenza specificata nel dizionario ros
            ).send()
        
    # !FASE 3: Conclusione della ricerca e invio del riassunto finale all'utente
    # Alla fine del ciclo, invia il riassunto finale all'utente
    # running_summary contiene il riassunto finale che è stato accumulato durante i cicli di ricerca
    # Invia un messaggio all'utente con il riassunto finale
    await cl.Message(
        author="segugio_assistant",
        content=f"Risposta alla tua domanda:\n\n {message.content}\n\n Risposta finale:\n\n {running_summary}."
        ).send()
    