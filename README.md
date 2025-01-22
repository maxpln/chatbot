# chatbot

L'objectif est de créer une interface graphique afin de requêter un LLM.

## Interface graphique

L'interface graphique et la gestion du chatbot va être construit avec Chainlit.

````bash
cd backend
chainlit run cl_app.py -w
````

Les variables d'environnement sont définies dans le fichier `.env` dans le dossier backend.

## LLM

### Ollama

```bash
ollama run deepseek-r1:1.5b
```


