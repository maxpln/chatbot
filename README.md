# chatbot

L'objectif est de créer une interface graphique afin de requêter un LLM.

## Interface graphique

L'interface graphique et la gestion du chatbot va être construit avec Chainlit.

````bash
cd backend
chainlit run cl_app.py -w
````

La persitstence des données est gérée avec LiteralAI : https://docs.chainlit.io/llmops/literalai

Les variables d'environnement sont définies dans le fichier `.env` dans le dossier backend.

Choix des icones : https://lucide.dev/icons/

## LLM

### Ollama

```bash
ollama run deepseek-r1:1.5b
```


