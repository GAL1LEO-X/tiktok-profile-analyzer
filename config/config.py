import os
from dotenv import load_dotenv

# Carica le variabili d'ambiente
load_dotenv()

# Configurazioni TikTok
TIKTOK_USERNAME = os.getenv('TIKTOK_USERNAME')
TIKTOK_PASSWORD = os.getenv('TIKTOK_PASSWORD')

# Configurazione OpenAI
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GPT_MODEL = "gpt-4"

# Configurazioni Database
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./tiktok_analyzer.db')

# Configurazioni API
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', 8000))
API_DEBUG = bool(os.getenv('API_DEBUG', True))

# Configurazioni Scraping
SCRAPING_INTERVAL = int(os.getenv('SCRAPING_INTERVAL', 3600))  # in secondi
MAX_POSTS_PER_PROFILE = int(os.getenv('MAX_POSTS_PER_PROFILE', 50))
BROWSER_HEADLESS = bool(os.getenv('BROWSER_HEADLESS', True))

# Configurazioni Analisi
SENTIMENT_THRESHOLD = float(os.getenv('SENTIMENT_THRESHOLD', 0.3))
ENGAGEMENT_RATE_THRESHOLD = float(os.getenv('ENGAGEMENT_RATE_THRESHOLD', 0.02))
MIN_INTERACTIONS_THRESHOLD = int(os.getenv('MIN_INTERACTIONS_THRESHOLD', 5))

# Configurazioni Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = 'logs/tiktok_analyzer.log'

# Configurazioni Cache
CACHE_TTL = int(os.getenv('CACHE_TTL', 3600))  # in secondi
CACHE_TYPE = os.getenv('CACHE_TYPE', 'simple')

# Configurazioni Security
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configurazioni Rate Limiting
RATE_LIMIT_CALLS = int(os.getenv('RATE_LIMIT_CALLS', 100))
RATE_LIMIT_PERIOD = int(os.getenv('RATE_LIMIT_PERIOD', 3600))  # in secondi

# Configurazioni AI
AI_ANALYSIS_BATCH_SIZE = int(os.getenv('AI_ANALYSIS_BATCH_SIZE', 10))
TRENDING_TOPICS_MIN_OCCURRENCES = int(os.getenv('TRENDING_TOPICS_MIN_OCCURRENCES', 3))
REPUTATION_RISK_THRESHOLD = float(os.getenv('REPUTATION_RISK_THRESHOLD', 0.7))

# Configurazioni Dashboard
DASHBOARD_UPDATE_INTERVAL = int(os.getenv('DASHBOARD_UPDATE_INTERVAL', 300))  # in secondi
DASHBOARD_MAX_DATAPOINTS = int(os.getenv('DASHBOARD_MAX_DATAPOINTS', 1000))

# Paths
INPUT_FILE_PATH = 'data/profiles.txt'
OUTPUT_DIR = 'data/output'
CACHE_DIR = 'data/cache'
MODEL_DIR = 'data/models'

# Assicura che le directory necessarie esistano
for directory in [OUTPUT_DIR, CACHE_DIR, MODEL_DIR, 'logs']:
    os.makedirs(directory, exist_ok=True) 