# Aulab Segugio


**Descrizione dell'Applicativo**


Aulab Segugio è un assistente di ricerca intelligente che utilizza l'AI per condurre ricerche web approfondite e iterative. L'applicativo è progettato per eseguire ricerche complesse attraverso un processo ciclico di query, analisi e approfondimento, utilizzando una combinazione di API di OpenAI per l'elaborazione del linguaggio naturale e Tavily per la ricerca web.


L'applicativo si distingue per la sua capacità di raffinare progressivamente le ricerche attraverso cicli di apprendimento. Partendo da una domanda iniziale dell'utente, il sistema genera query ottimizzate, raccoglie informazioni da fonti web, sintetizza i risultati e identifica automaticamente aree che necessitano di ulteriore approfondimento, creando un processo di ricerca dinamico e approfondito.


La forza di questo sistema risiede nella sua capacità di simulare il processo di ricerca umano, dove ogni risultato porta a nuove domande e approfondimenti. L'applicativo utilizza un'architettura modulare che separa le diverse fasi del processo di ricerca - dalla generazione delle query all'analisi dei risultati - permettendo una ricerca sistematica e approfondita su qualsiasi argomento.


**Manuale Tecnico di Funzionamento**


1. Avvio e Configurazione
   - L'applicativo si inizializza caricando le configurazioni per l'API di OpenAI
   - Si possono utilizzare due configurazioni: una locale con LLM (Large Language Model) e una cloud con OpenAI
   - Il sistema utilizza Chainlit per l'interfaccia utente interattiva


2. Processo di Ricerca
   - Input Utente: L'utente inserisce una domanda o un tema di ricerca
   - Generazione Query: Il sistema ottimizza la domanda dell'utente in una query di ricerca efficace
   - Ricerca Web: Utilizza l'API Tavily per cercare informazioni pertinenti online
   - Sintesi: Le informazioni trovate vengono sintetizzate in un riassunto coerente
   - Analisi: Il sistema identifica lacune nelle informazioni raccolte
   - Iterazione: Genera nuove domande per approfondire gli aspetti mancanti


3. Ciclo di Approfondimento
   - Il sistema esegue fino a 4 o n cicli di ricerca
   - In ogni ciclo:
     * Esegue la ricerca web con la query corrente
     * Aggiorna il riassunto con le nuove informazioni
     * Analizza il riassunto per identificare lacune
     * Genera una nuova query di approfondimento


4. Output e Comunicazione
   - Il sistema fornisce feedback continuo all'utente durante la ricerca
   - Mostra le fonti trovate e i riassunti parziali
   - Spiega le motivazioni dietro ogni nuova direzione di ricerca
   - Alla fine presenta un riassunto completo e strutturato


5. Gestione dei Prompt
   - Utilizza tre tipi di prompt specializzati:
     * Query Writer: Per ottimizzare le query di ricerca
     * Summarizer: Per sintetizzare le informazioni
     * Reflection: Per analizzare e identificare aree di approfondimento


6. Sistema di Risposta
   - Le risposte vengono formattate in modo coerente e strutturato
   - Ogni passaggio della ricerca viene documentato e comunicato
