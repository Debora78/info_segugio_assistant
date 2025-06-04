# inizializzare il sistema
# importa la libreria Chainlit con nome abbreviato 'cl'
import chainlit as cl

# importa la libreria OpenAI per interagire con il modello di intelligenza artificiale
from openai import OpenAI

#inizializzazione del Client OpenAI con le configurazioni 
client = OpenAI(base_url=Config.AI_API_URL, api_key=Config.AI_API_KEY)


# con questo decoratore diciamo che ogni volta che viene ricevuto un messaggio dall'interfaccia, viene chiamata la funzione main
# in message metti le informazioni che l'utente ha scritto 
@cl.on_message
async def main(message: cl.Message):
    # Your custom logic goes here...

    # Send a response back to the user
    # Con questo comando riesce ad inviare all'interfaccia chainlit una risposta che ripropone il messaggio dell'utente
    await cl.Message(
        content=f"Received: {message.content}",
    ).send()