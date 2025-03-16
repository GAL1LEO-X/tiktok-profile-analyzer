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

## Setup Locale

1. Clona il repository:
```bash
git clone https://github.com/GAL1LEO-X/tiktok-profile-analyzer.git
cd tiktok-profile-analyzer
```

2. Installa le dipendenze:
```bash
pip install -r requirements.txt
```

3. Configura le variabili d'ambiente nel file `.env`

4. Avvia l'applicazione:
```bash
python src/main.py
```

## Setup su Replit

1. Vai su [Replit](https://replit.com)
2. Clicca su "+ Create Repl"
3. Scegli "Import from GitHub"
4. Inserisci l'URL: `https://github.com/GAL1LEO-X/tiktok-profile-analyzer`
5. Configura le variabili d'ambiente nella sezione Secrets:
   - `OPENAI_API_KEY`
   - `DATABASE_URL`
   - `API_HOST`
   - `API_PORT`
   - E altre variabili necessarie
6. Clicca su "Run" per avviare l'applicazione

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

1. Aggiungi i profili da analizzare in `data/profiles.txt`
2. Accedi alla dashboard all'indirizzo principale dell'applicazione
3. Visualizza l'API documentation su `/api/docs`

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