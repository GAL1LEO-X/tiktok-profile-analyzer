import asyncio
import logging
from pathlib import Path
import sys
import os

# Aggiungi la directory root al path di Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import (
    INPUT_FILE_PATH,
    OUTPUT_DIR,
    CACHE_DIR,
    MODEL_DIR,
    LOG_LEVEL,
    LOG_FORMAT,
    LOG_FILE
)

from src.scraper.tiktok_scraper import TikTokScraper
from src.analyzer.ai_analyzer import AIAnalyzer
from src.api.main import app

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TikTokAnalyzer:
    def __init__(self):
        self.scraper = None
        self.analyzer = AIAnalyzer()
        
        # Assicura che tutte le directory necessarie esistano
        for directory in [OUTPUT_DIR, CACHE_DIR, MODEL_DIR]:
            Path(directory).mkdir(parents=True, exist_ok=True)

    async def init_scraper(self):
        """Inizializza lo scraper"""
        self.scraper = TikTokScraper()
        await self.scraper.init_browser()
        await self.scraper.login()

    async def close_scraper(self):
        """Chiude lo scraper"""
        if self.scraper:
            await self.scraper.close()

    async def analyze_profiles(self, usernames: list[str]):
        """Analizza una lista di profili"""
        try:
            for username in usernames:
                logger.info(f"Starting analysis for profile: {username}")
                
                # Scraping del profilo
                try:
                    profile_data = await self.scraper.analyze_profile(username)
                    logger.info(f"Scraping completed for {username}")
                except Exception as e:
                    logger.error(f"Error scraping profile {username}: {str(e)}")
                    continue

                # Analisi AI del profilo
                try:
                    report = await self.analyzer.generate_profile_report(username)
                    logger.info(f"AI analysis completed for {username}")
                except Exception as e:
                    logger.error(f"Error analyzing profile {username}: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"Error in profile analysis: {str(e)}")
        finally:
            await self.close_scraper()

async def main():
    """Funzione principale"""
    try:
        # Verifica se il file di input esiste
        if not Path(INPUT_FILE_PATH).exists():
            logger.error(f"Input file not found: {INPUT_FILE_PATH}")
            return

        # Legge gli username da analizzare
        with open(INPUT_FILE_PATH, 'r') as f:
            usernames = [line.strip() for line in f if line.strip()]

        if not usernames:
            logger.error("No usernames found in input file")
            return

        # Inizializza l'analizzatore
        analyzer = TikTokAnalyzer()
        await analyzer.init_scraper()

        # Avvia l'analisi
        await analyzer.analyze_profiles(usernames)

    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")

def run_api():
    """Avvia il server API"""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='TikTok Profile Analyzer')
    parser.add_argument('--mode', choices=['scrape', 'api'], default='scrape',
                      help='Modalità di esecuzione: scrape per analizzare profili, api per avviare il server')
    
    args = parser.parse_args()
    
    if args.mode == 'api':
        run_api()
    else:
        asyncio.run(main()) 