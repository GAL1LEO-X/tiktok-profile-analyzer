from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import json
from pathlib import Path
from datetime import datetime, timedelta
import asyncio
import logging

from config.config import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    OUTPUT_DIR
)

from src.scraper.tiktok_scraper import TikTokScraper
from src.analyzer.ai_analyzer import AIAnalyzer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TikTok Profile Analyzer API",
    description="API per l'analisi di profili TikTok con AI",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Pydantic models
class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str
    disabled: Optional[bool] = None

class ProfileRequest(BaseModel):
    username: str

class AnalysisRequest(BaseModel):
    username: str
    analysis_type: str

# Utility functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return User(username=username)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# Background task functions
async def scrape_profile(username: str):
    try:
        scraper = TikTokScraper()
        await scraper.init_browser()
        await scraper.login()
        await scraper.analyze_profile(username)
        await scraper.close()
    except Exception as e:
        logger.error(f"Error scraping profile {username}: {str(e)}")

async def analyze_profile(username: str):
    try:
        analyzer = AIAnalyzer()
        await analyzer.generate_profile_report(username)
    except Exception as e:
        logger.error(f"Error analyzing profile {username}: {str(e)}")

# API endpoints
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Implementa qui la tua logica di autenticazione
    user = User(username=form_data.username)
    access_token = create_access_token({"sub": user.username})
    return Token(access_token=access_token, token_type="bearer")

@app.post("/profiles/analyze")
async def analyze_tiktok_profile(
    request: ProfileRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Avvia l'analisi di un profilo TikTok
    """
    try:
        # Aggiunge i task in background
        background_tasks.add_task(scrape_profile, request.username)
        background_tasks.add_task(analyze_profile, request.username)
        
        return {
            "status": "success",
            "message": f"Analysis started for profile @{request.username}",
            "username": request.username
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/profiles/{username}/status")
async def get_profile_status(
    username: str,
    current_user: User = Depends(get_current_user)
):
    """
    Controlla lo stato dell'analisi di un profilo
    """
    try:
        output_dir = Path(OUTPUT_DIR)
        profile_files = list(output_dir.glob(f"{username}_*.json"))
        report_files = list(output_dir.glob(f"{username}_report_*.json"))

        return {
            "username": username,
            "data_collected": len(profile_files) > 0,
            "analysis_completed": len(report_files) > 0,
            "last_update": max([f.stat().st_mtime for f in profile_files + report_files]) if profile_files or report_files else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/profiles/{username}/report")
async def get_profile_report(
    username: str,
    current_user: User = Depends(get_current_user)
):
    """
    Ottiene il report completo di un profilo
    """
    try:
        output_dir = Path(OUTPUT_DIR)
        report_files = list(output_dir.glob(f"{username}_report_*.json"))
        
        if not report_files:
            raise HTTPException(status_code=404, detail="Report not found")
        
        latest_report = max(report_files, key=lambda f: f.stat().st_mtime)
        
        with open(latest_report, 'r', encoding='utf-8') as f:
            report = json.load(f)
            
        return report
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/profiles/{username}/metrics/{metric_type}")
async def get_profile_metrics(
    username: str,
    metric_type: str,
    current_user: User = Depends(get_current_user)
):
    """
    Ottiene metriche specifiche per un profilo
    """
    try:
        output_dir = Path(OUTPUT_DIR)
        report_files = list(output_dir.glob(f"{username}_report_*.json"))
        
        if not report_files:
            raise HTTPException(status_code=404, detail="Report not found")
        
        latest_report = max(report_files, key=lambda f: f.stat().st_mtime)
        
        with open(latest_report, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        if metric_type not in report['raw_data']:
            raise HTTPException(status_code=404, detail=f"Metric type {metric_type} not found")
            
        return report['raw_data'][metric_type]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/profiles")
async def list_profiles(current_user: User = Depends(get_current_user)):
    """
    Lista tutti i profili analizzati
    """
    try:
        output_dir = Path(OUTPUT_DIR)
        profile_files = list(output_dir.glob('*_[0-9]*.json'))
        profiles = set(f.stem.split('_')[0] for f in profile_files)
        
        return {
            "profiles": list(profiles),
            "count": len(profiles)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 