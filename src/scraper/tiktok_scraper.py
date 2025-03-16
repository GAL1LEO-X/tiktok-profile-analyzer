import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Browser, Page
import json
import os
from pathlib import Path

from config.config import (
    TIKTOK_USERNAME,
    TIKTOK_PASSWORD,
    BROWSER_HEADLESS,
    MAX_POSTS_PER_PROFILE,
    OUTPUT_DIR,
    CACHE_DIR
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TikTokScraper:
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.cache_dir = Path(CACHE_DIR)
        self.output_dir = Path(OUTPUT_DIR)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def init_browser(self):
        """Inizializza il browser Playwright"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=BROWSER_HEADLESS)
        self.page = await self.browser.new_page()
        await self.page.set_viewport_size({"width": 1920, "height": 1080})

    async def login(self):
        """Effettua il login su TikTok"""
        try:
            await self.page.goto('https://www.tiktok.com/login')
            # Implementa qui la logica di login
            # Nota: TikTok potrebbe richiedere verifiche aggiuntive
            await self.page.fill('input[name="username"]', TIKTOK_USERNAME)
            await self.page.fill('input[name="password"]', TIKTOK_PASSWORD)
            await self.page.click('button[type="submit"]')
            await self.page.wait_for_load_state('networkidle')
            
            # Verifica se il login è avvenuto con successo
            if await self.page.query_selector('.login-error'):
                raise Exception("Login failed")
            
            logger.info("Login successful")
            
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            raise

    async def get_profile_info(self, username: str) -> Dict:
        """Ottiene le informazioni del profilo"""
        try:
            await self.page.goto(f'https://www.tiktok.com/@{username}')
            await self.page.wait_for_load_state('networkidle')

            profile_info = await self.page.evaluate('''() => {
                const info = {};
                info.username = document.querySelector('h1.tiktok-1d3qdok').innerText;
                info.bio = document.querySelector('h2.tiktok-1d3qdok')?.innerText || '';
                info.followers = document.querySelector('strong[title="Followers"]').innerText;
                info.following = document.querySelector('strong[title="Following"]').innerText;
                info.likes = document.querySelector('strong[title="Likes"]').innerText;
                return info;
            }''')

            return profile_info

        except Exception as e:
            logger.error(f"Error getting profile info for {username}: {str(e)}")
            return {}

    async def get_recent_posts(self, username: str, max_posts: int = MAX_POSTS_PER_PROFILE) -> List[Dict]:
        """Ottiene i post recenti di un profilo"""
        try:
            await self.page.goto(f'https://www.tiktok.com/@{username}')
            await self.page.wait_for_load_state('networkidle')

            posts = await self.page.evaluate(f'''() => {{
                const posts = [];
                const videoElements = document.querySelectorAll('div[data-e2e="user-post-item"]');
                
                for (let i = 0; i < Math.min(videoElements.length, {max_posts}); i++) {{
                    const video = videoElements[i];
                    posts.push({{
                        url: video.querySelector('a').href,
                        thumbnail: video.querySelector('img')?.src || '',
                        description: video.querySelector('div[data-e2e="user-post-item-desc"]')?.innerText || '',
                        likes: video.querySelector('strong[data-e2e="like-count"]')?.innerText || '0',
                        comments: video.querySelector('strong[data-e2e="comment-count"]')?.innerText || '0',
                        shares: video.querySelector('strong[data-e2e="share-count"]')?.innerText || '0',
                        date: video.querySelector('time')?.dateTime || ''
                    }});
                }}
                return posts;
            }}''')

            return posts

        except Exception as e:
            logger.error(f"Error getting posts for {username}: {str(e)}")
            return []

    async def get_post_interactions(self, post_url: str) -> Dict:
        """Analizza le interazioni di un singolo post"""
        try:
            await self.page.goto(post_url)
            await self.page.wait_for_load_state('networkidle')

            interactions = await self.page.evaluate('''() => {
                const interactions = {};
                interactions.comments = [];
                
                // Raccoglie i commenti
                const commentElements = document.querySelectorAll('div[data-e2e="comment-item"]');
                for (const comment of commentElements) {
                    interactions.comments.push({
                        username: comment.querySelector('.user-username')?.innerText || '',
                        text: comment.querySelector('.comment-text')?.innerText || '',
                        likes: comment.querySelector('.comment-like-count')?.innerText || '0',
                        date: comment.querySelector('time')?.dateTime || ''
                    });
                }
                
                return interactions;
            }''')

            return interactions

        except Exception as e:
            logger.error(f"Error getting interactions for post {post_url}: {str(e)}")
            return {}

    def save_to_cache(self, data: Dict, filename: str):
        """Salva i dati nella cache"""
        try:
            cache_file = self.cache_dir / filename
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving to cache: {str(e)}")

    def load_from_cache(self, filename: str) -> Optional[Dict]:
        """Carica i dati dalla cache"""
        try:
            cache_file = self.cache_dir / filename
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading from cache: {str(e)}")
        return None

    async def analyze_profile(self, username: str) -> Dict:
        """Analizza un profilo completo"""
        profile_data = {
            'username': username,
            'timestamp': datetime.now().isoformat(),
            'profile_info': {},
            'posts': [],
            'interactions': {}
        }

        try:
            # Ottiene le informazioni del profilo
            profile_data['profile_info'] = await self.get_profile_info(username)
            
            # Ottiene i post recenti
            posts = await self.get_recent_posts(username)
            profile_data['posts'] = posts

            # Analizza le interazioni per ogni post
            for post in posts:
                post_url = post['url']
                interactions = await self.get_post_interactions(post_url)
                profile_data['interactions'][post_url] = interactions

            # Salva i dati nella cache
            cache_filename = f"{username}_{datetime.now().strftime('%Y%m%d')}.json"
            self.save_to_cache(profile_data, cache_filename)

            # Salva i dati nella directory di output
            output_filename = self.output_dir / cache_filename
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, ensure_ascii=False, indent=2)

            return profile_data

        except Exception as e:
            logger.error(f"Error analyzing profile {username}: {str(e)}")
            return profile_data

    async def close(self):
        """Chiude il browser"""
        if self.browser:
            await self.browser.close()

async def main():
    scraper = TikTokScraper()
    try:
        await scraper.init_browser()
        await scraper.login()
        
        # Leggi gli username da analizzare dal file
        with open(os.path.join(OUTPUT_DIR, 'profiles.txt'), 'r') as f:
            usernames = [line.strip() for line in f if line.strip()]

        # Analizza ogni profilo
        for username in usernames:
            logger.info(f"Analyzing profile: {username}")
            await scraper.analyze_profile(username)

    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
    finally:
        await scraper.close()

if __name__ == "__main__":
    asyncio.run(main()) 