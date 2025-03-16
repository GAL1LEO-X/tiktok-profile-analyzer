import logging
from typing import Dict, List, Tuple
import json
from pathlib import Path
import openai
from textblob import TextBlob
from collections import Counter
from datetime import datetime, timedelta

from config.config import (
    OPENAI_API_KEY,
    GPT_MODEL,
    SENTIMENT_THRESHOLD,
    ENGAGEMENT_RATE_THRESHOLD,
    TRENDING_TOPICS_MIN_OCCURRENCES,
    REPUTATION_RISK_THRESHOLD,
    OUTPUT_DIR
)

openai.api_key = OPENAI_API_KEY
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIAnalyzer:
    def __init__(self):
        self.output_dir = Path(OUTPUT_DIR)

    async def analyze_sentiment(self, text: str) -> Dict:
        """Analizza il sentiment del testo usando TextBlob e GPT-4"""
        try:
            # Analisi base con TextBlob
            blob = TextBlob(text)
            basic_sentiment = blob.sentiment.polarity

            # Analisi avanzata con GPT-4
            response = await openai.ChatCompletion.acreate(
                model=GPT_MODEL,
                messages=[
                    {"role": "system", "content": "Analizza il sentiment e il mood del seguente testo, fornendo un'analisi dettagliata."},
                    {"role": "user", "content": text}
                ]
            )

            return {
                'basic_sentiment': basic_sentiment,
                'detailed_analysis': response.choices[0].message['content'],
                'is_negative': basic_sentiment < -SENTIMENT_THRESHOLD
            }

        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}")
            return {'error': str(e)}

    async def analyze_engagement(self, profile_data: Dict) -> Dict:
        """Calcola e analizza l'engagement rate"""
        try:
            total_followers = int(profile_data['profile_info']['followers'].replace('K', '000').replace('M', '000000'))
            
            engagement_metrics = []
            for post in profile_data['posts']:
                likes = int(post['likes'].replace('K', '000').replace('M', '000000'))
                comments = int(post['comments'].replace('K', '000').replace('M', '000000'))
                shares = int(post['shares'].replace('K', '000').replace('M', '000000'))
                
                engagement_rate = (likes + comments + shares) / total_followers
                engagement_metrics.append({
                    'post_url': post['url'],
                    'engagement_rate': engagement_rate,
                    'metrics': {
                        'likes': likes,
                        'comments': comments,
                        'shares': shares
                    }
                })

            # Analisi con GPT-4
            avg_engagement = sum(m['engagement_rate'] for m in engagement_metrics) / len(engagement_metrics)
            engagement_analysis = await openai.ChatCompletion.acreate(
                model=GPT_MODEL,
                messages=[
                    {"role": "system", "content": "Analizza le metriche di engagement e fornisci insights strategici."},
                    {"role": "user", "content": f"Analizza questi dati di engagement: {json.dumps(engagement_metrics)}"}
                ]
            )

            return {
                'metrics': engagement_metrics,
                'average_engagement': avg_engagement,
                'analysis': engagement_analysis.choices[0].message['content'],
                'is_performing_well': avg_engagement > ENGAGEMENT_RATE_THRESHOLD
            }

        except Exception as e:
            logger.error(f"Error in engagement analysis: {str(e)}")
            return {'error': str(e)}

    async def identify_trending_topics(self, profile_data: Dict) -> Dict:
        """Identifica i trending topics nei contenuti"""
        try:
            # Raccoglie tutto il testo dei post
            all_content = ' '.join([post['description'] for post in profile_data['posts']])
            
            # Analisi con GPT-4
            response = await openai.ChatCompletion.acreate(
                model=GPT_MODEL,
                messages=[
                    {"role": "system", "content": "Identifica i principali trend e topic ricorrenti nel contenuto."},
                    {"role": "user", "content": all_content}
                ]
            )

            # Estrae hashtag
            hashtags = [word for word in all_content.split() if word.startswith('#')]
            hashtag_counts = Counter(hashtags)
            trending_hashtags = {tag: count for tag, count in hashtag_counts.items() 
                               if count >= TRENDING_TOPICS_MIN_OCCURRENCES}

            return {
                'trending_topics': response.choices[0].message['content'],
                'hashtag_analysis': trending_hashtags,
                'content_themes': await self._analyze_content_themes(all_content)
            }

        except Exception as e:
            logger.error(f"Error in trending topics analysis: {str(e)}")
            return {'error': str(e)}

    async def _analyze_content_themes(self, content: str) -> Dict:
        """Analizza i temi principali del contenuto"""
        try:
            response = await openai.ChatCompletion.acreate(
                model=GPT_MODEL,
                messages=[
                    {"role": "system", "content": "Identifica e categorizza i principali temi del contenuto."},
                    {"role": "user", "content": content}
                ]
            )
            
            return json.loads(response.choices[0].message['content'])
        except Exception as e:
            logger.error(f"Error in content theme analysis: {str(e)}")
            return {}

    async def analyze_reputation_risks(self, profile_data: Dict) -> Dict:
        """Analizza potenziali rischi reputazionali"""
        try:
            # Raccoglie contenuti e commenti
            all_content = []
            for post in profile_data['posts']:
                all_content.append(post['description'])
                post_url = post['url']
                if post_url in profile_data['interactions']:
                    comments = profile_data['interactions'][post_url].get('comments', [])
                    all_content.extend([comment['text'] for comment in comments])

            content_for_analysis = '\n'.join(all_content)

            # Analisi con GPT-4
            response = await openai.ChatCompletion.acreate(
                model=GPT_MODEL,
                messages=[
                    {"role": "system", "content": "Analizza il contenuto per identificare potenziali rischi reputazionali, controversie o feedback negativi."},
                    {"role": "user", "content": content_for_analysis}
                ]
            )

            # Analisi del sentiment generale
            sentiment_scores = [TextBlob(text).sentiment.polarity for text in all_content]
            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0

            return {
                'risk_analysis': response.choices[0].message['content'],
                'average_sentiment': avg_sentiment,
                'risk_level': 'high' if avg_sentiment < -REPUTATION_RISK_THRESHOLD else 'medium' if avg_sentiment < 0 else 'low',
                'negative_content_percentage': len([s for s in sentiment_scores if s < -SENTIMENT_THRESHOLD]) / len(sentiment_scores) if sentiment_scores else 0
            }

        except Exception as e:
            logger.error(f"Error in reputation risk analysis: {str(e)}")
            return {'error': str(e)}

    async def analyze_profile_interactions(self, profile_data: Dict) -> Dict:
        """Analizza le interazioni tra profili"""
        try:
            interactions = {}
            mentioned_users = set()
            
            # Raccoglie menzioni e interazioni
            for post in profile_data['posts']:
                post_url = post['url']
                if post_url in profile_data['interactions']:
                    comments = profile_data['interactions'][post_url].get('comments', [])
                    for comment in comments:
                        username = comment['username']
                        if username not in interactions:
                            interactions[username] = {
                                'comment_count': 0,
                                'total_likes': 0,
                                'last_interaction': None
                            }
                        
                        interactions[username]['comment_count'] += 1
                        interactions[username]['total_likes'] += int(comment['likes'].replace('K', '000').replace('M', '000000'))
                        interactions[username]['last_interaction'] = comment['date']

                # Estrae menzioni dal testo del post
                words = post['description'].split()
                mentions = [word for word in words if word.startswith('@')]
                mentioned_users.update(mentions)

            # Analisi con GPT-4
            interaction_analysis = await openai.ChatCompletion.acreate(
                model=GPT_MODEL,
                messages=[
                    {"role": "system", "content": "Analizza il pattern di interazioni tra i profili e identifica relazioni significative."},
                    {"role": "user", "content": f"Analizza queste interazioni: {json.dumps(interactions)}"}
                ]
            )

            return {
                'interactions': interactions,
                'mentioned_users': list(mentioned_users),
                'analysis': interaction_analysis.choices[0].message['content'],
                'top_interactors': sorted(
                    interactions.items(),
                    key=lambda x: x[1]['comment_count'],
                    reverse=True
                )[:10]
            }

        except Exception as e:
            logger.error(f"Error in interaction analysis: {str(e)}")
            return {'error': str(e)}

    async def generate_profile_report(self, username: str) -> Dict:
        """Genera un report completo per un profilo"""
        try:
            # Carica i dati del profilo
            profile_file = list(self.output_dir.glob(f"{username}_*.json"))[-1]
            with open(profile_file, 'r', encoding='utf-8') as f:
                profile_data = json.load(f)

            # Esegue tutte le analisi
            sentiment_analysis = await self.analyze_sentiment(' '.join([post['description'] for post in profile_data['posts']]))
            engagement_analysis = await self.analyze_engagement(profile_data)
            trending_topics = await self.identify_trending_topics(profile_data)
            reputation_risks = await self.analyze_reputation_risks(profile_data)
            interaction_analysis = await self.analyze_profile_interactions(profile_data)

            # Genera il report finale con GPT-4
            report_data = {
                'profile_info': profile_data['profile_info'],
                'sentiment': sentiment_analysis,
                'engagement': engagement_analysis,
                'trending_topics': trending_topics,
                'reputation_risks': reputation_risks,
                'interactions': interaction_analysis
            }

            final_analysis = await openai.ChatCompletion.acreate(
                model=GPT_MODEL,
                messages=[
                    {"role": "system", "content": "Genera un report dettagliato e professionale basato sui dati di analisi del profilo TikTok."},
                    {"role": "user", "content": f"Genera un report completo basato su questi dati: {json.dumps(report_data)}"}
                ]
            )

            report = {
                'timestamp': datetime.now().isoformat(),
                'username': username,
                'raw_data': report_data,
                'executive_summary': final_analysis.choices[0].message['content']
            }

            # Salva il report
            report_file = self.output_dir / f"{username}_report_{datetime.now().strftime('%Y%m%d')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)

            return report

        except Exception as e:
            logger.error(f"Error generating report for {username}: {str(e)}")
            return {'error': str(e)}

async def main():
    analyzer = AIAnalyzer()
    try:
        # Trova tutti i profili analizzati
        profile_files = list(Path(OUTPUT_DIR).glob('*_[0-9]*.json'))
        usernames = set(f.stem.split('_')[0] for f in profile_files)

        # Genera report per ogni profilo
        for username in usernames:
            logger.info(f"Generating report for {username}")
            await analyzer.generate_profile_report(username)

    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 