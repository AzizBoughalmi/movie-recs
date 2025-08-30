from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import os
import requests
import logging
import time
from dotenv import load_dotenv

from pathlib import Path
from typing import Optional
from pydantic import BaseModel


from .agent import get_movie_recommendations

# Configuration du logging pour FastAPI
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()

# Modèles Pydantic
class RecommendationRequest(BaseModel):
    favorites: list[str]
    query: Optional[str] = None

# CORS
origins = ["http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Force le chemin vers le .env
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
print("TMDB_API_KEY =", TMDB_API_KEY)  # Debug
TMDB_BASE_URL = "https://api.themoviedb.org/3"

@app.get("/ping")
def ping():
    return {"message": "pong"}

@app.get("/search")
def search_movies(query: str = Query(..., min_length=1)):
    """Recherche films ou séries via TMDB"""
    logger.info(f"🔍 API CALL - /search: query='{query}'")
    
    url = f"{TMDB_BASE_URL}/search/multi"
    params = {
        "api_key": TMDB_API_KEY,
        "query": query,
        "language": "fr-FR"  # ou "en-US"
    }
    
    logger.debug(f"📤 TMDB Request: {url}")
    logger.debug(f"📤 Params: {params}")
    
    start_time = time.time()
    response = requests.get(url, params=params)
    end_time = time.time()
    
    logger.info(f"⏱️ TMDB Response Time: {end_time - start_time:.2f}s")
    logger.debug(f"📥 TMDB Status: {response.status_code}")
    
    if response.status_code != 200:
        logger.error(f"❌ TMDB API Error: {response.status_code}")
        return {"error": "TMDB API error"}
    
    data = response.json()
    logger.debug(f"📥 TMDB Raw Results: {len(data.get('results', []))} items")
    
    # On ne garde que les champs utiles
    results = []
    for item in data.get("results", []):
        results.append({
            "id": item.get("id"),
            "title": item.get("title") or item.get("name"),
            "media_type": item.get("media_type"),
            "poster_path": f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}" if item.get("poster_path") else None,
            "release_date": item.get("release_date") or item.get("first_air_date")
        })
    
    logger.info(f"✅ Search Results: Returning {len(results)} processed items")
    for i, item in enumerate(results[:3]):  # Log first 3 results
        logger.debug(f"  {i+1}. {item.get('title')} ({item.get('media_type')})")
    
    return results

@app.post("/recommendations")
def get_recommendations(request: RecommendationRequest):
    """
    Obtient des recommandations de films basées sur les favoris de l'utilisateur
    
    Args:
        request: Requête contenant les favoris et la requête optionnelle
    
    Returns:
        Recommandations de films structurées
    """
    logger.info(f"🎯 API CALL - /recommendations")
    logger.info(f"📝 Favorites received: {request.favorites}")
    logger.info(f"💭 Custom query: {request.query}")
    
    start_time = time.time()
    
    try:
        logger.info(f"🚀 Starting AI recommendation process...")
        recommendations = get_movie_recommendations(request.favorites, request.query)
        
        end_time = time.time()
        logger.info(f"⏱️ Total API Processing Time: {end_time - start_time:.2f}s")
        logger.info(f"✅ RECOMMENDATIONS API SUCCESS")
        
        return recommendations
        
    except Exception as e:
        end_time = time.time()
        logger.error(f"❌ RECOMMENDATIONS API ERROR after {end_time - start_time:.2f}s")
        logger.error(f"❌ Error details: {str(e)}")
        logger.exception("Full error traceback:")
        
        return {"error": f"Erreur lors de la génération des recommandations: {str(e)}"}
