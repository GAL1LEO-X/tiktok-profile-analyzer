# TikTok Profile Analyzer

Un potente strumento di analisi per profili TikTok che combina web scraping e analisi AI per fornire insights dettagliati sui profili e le loro interazioni.

## Caratteristiche Principali

- Scraping automatizzato di profili TikTok
- Analisi giornaliera dei post
- Analisi dettagliata delle interazioni tra profili
- Calcolo dell'Engagement Rate
- Analisi del sentiment e mood
- Identificazione dei Trending Topics
- Monitoraggio della reputazione
- Integrazione con GPT-4 per analisi avanzate
- Dashboard interattiva per la visualizzazione dei dati

## Setup su Replit

1. Crea un nuovo progetto Python su Replit
2. Clona questo repository:
   ```bash
   git clone <repository-url>
   ```
3. Nel file Secrets di Replit, aggiungi le seguenti variabili:
   - `TIKTOK_USERNAME`: Il tuo username TikTok
   - `TIKTOK_PASSWORD`: La tua password TikTok
   - `OPENAI_API_KEY`: La tua API key di OpenAI

4. Nel shell di Replit, esegui:
   ```bash
   pip install -r requirements.txt
   playwright install
   python -m textblob.download_corpora
   ```

## Struttura del Progetto

```
├── src/
│   ├── scraper/         # Moduli per lo scraping di TikTok
│   ├── analyzer/        # Analisi AI e processing dei dati
│   ├── api/            # API FastAPI
│   ├── database/       # Gestione del database
│   └── dashboard/      # Dashboard interattiva
├── tests/             # Test unitari e di integrazione
├── data/             # Directory per i dati
├── config/          # File di configurazione
└── logs/           # Log del sistema
```

## Utilizzo

1. Prepara un file di testo con gli username TikTok da analizzare:
   ```
   @username1
   @username2
   @username3
   ```

2. Avvia l'applicazione:
   ```bash
   python src/main.py
   ```

3. Accedi alla dashboard all'indirizzo: `http://localhost:8000`

## Funzionalità Dettagliate

### Analisi del Profilo
- Statistiche complete del profilo
- Trend di crescita
- Pattern di posting
- Analisi dei contenuti

### Analisi delle Interazioni
- Network di connessioni
- Frequenza di interazioni
- Tipologia di interazioni
- Influenza reciproca

### Metriche di Engagement
- Engagement Rate per post
- Trend temporali
- Comparazione con benchmark
- Analisi per tipo di contenuto

### Analisi AI
- Sentiment Analysis dei commenti
- Identificazione topic ricorrenti
- Previsioni trend
- Analisi del rischio reputazionale

## Sicurezza

- Gestione sicura delle credenziali
- Rate limiting per le API
- Logging completo delle operazioni
- Backup automatico dei dati

## Contribuire

Per contribuire al progetto:
1. Fai un fork del repository
2. Crea un branch per la tua feature
3. Committi le tue modifiche
4. Apri una Pull Request

## Licenza

MIT License

## Supporto

Per supporto e domande, apri una issue nel repository. 