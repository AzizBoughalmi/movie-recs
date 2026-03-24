from fastapi import FastAPI, Query, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import os
import requests
import logging
import time
import uuid
from dotenv import load_dotenv

from pathlib import Path
from typing import Optional
from pydantic import BaseModel


from app.core.recommender import MovieRecommender
from app.core.profile_creator import ProfileCreator
from app.models.profile import Profile
from app.services.profile_service import ProfileService
from app.utils.session_utils import get_or_create_session_id, get_session_id
from app.config.settings import settings

# Configuration du logging pour FastAPI
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()

# Configuration du middleware de session
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# Créer les instances des services
movie_recommender = MovieRecommender()
profile_creator = ProfileCreator()
profile_service = ProfileService()

# Modèles Pydantic pour les requêtes
class RecommendationRequest(BaseModel):
    favorites: list[str]
    query: Optional[str] = None

class ProfileCreateRequest(BaseModel):
    favorite_movies: list[str]


class ProfileRecommendationRequest(BaseModel):
    profile: Profile
    custom_query: Optional[str] = None

# CORS - Configure allowed origins
# When frontend and backend are on the same domain (Heroku), FRONTEND_URL may be empty
# In that case, allow the same origin (requests from same app domain)
cors_origins = []
if settings.FRONTEND_URL:
    cors_origins = [settings.FRONTEND_URL]
else:
    # When FRONTEND_URL is not set, we're likely in production with same-origin serving
    # Allow all origins as fallback (the frontend is served by this same server)
    cors_origins = ["*"]

logger.info(f"🔐 CORS Origins configured: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Force le chemin vers le .env
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

TMDB_API_KEY = settings.TMDB_API_KEY
TMDB_BASE_URL = settings.TMDB_BASE_URL

# Mount built React frontend as static files with SPA fallback
frontend_dist_path = Path(__file__).parent.parent.parent / "frontend" / "dist"
if frontend_dist_path.exists():
    logger.info(f"✅ Mounting frontend static files from {frontend_dist_path}")
    # Mount with html=True to serve index.html for unmatched routes (SPA fallback)
    app.mount("/", StaticFiles(directory=str(frontend_dist_path), html=True), name="static")
else:
    logger.warning(f"⚠️ Frontend dist folder not found at {frontend_dist_path}")
    logger.info("Frontend will not be served. (This is expected in development; build frontend with 'npm run build' in frontend/)")

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
        recommendations = movie_recommender.get_recommendations_legacy(request.favorites, request.query)
        
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

@app.post("/profile/create")
def create_user_profile_api(request: ProfileCreateRequest, http_request: Request):
    """
    Crée un profil cinématographique détaillé basé sur les films favoris de l'utilisateur
    
    Args:
        request: Requête contenant les films favoris
        http_request: Requête HTTP pour la gestion de session
    
    Returns:
        Dict contenant profile_id et profile
    """
    logger.info(f"👤 API CALL - /profile/create")
    logger.info(f"📝 Favorite movies: {request.favorite_movies}")

    start_time = time.time()
    
    try:
        # Récupérer ou créer une session
        session_id = get_or_create_session_id(http_request)
        
        logger.info(f"🚀 Starting profile creation process...")
        user_profile = profile_creator.create_user_profile(
            favorite_movies=request.favorite_movies,
        )
        
        # Générer un ID unique pour ce profil
        profile_id = profile_service.generate_profile_id()
        
        # Sauvegarder le profil dans la session
        profile_service.save_profile(session_id, profile_id, user_profile)
        
        end_time = time.time()
        logger.info(f"⏱️ Profile Creation Time: {end_time - start_time:.2f}s")
        logger.info(f"✅ PROFILE CREATION SUCCESS")
        logger.info(f"🆔 Profile ID: {profile_id}")
        logger.info(f"🔗 Session ID: {session_id}")
        logger.debug(f"📊 Profile created")
        logger.debug(f"🎬 Favorite genres: {user_profile.favorite_genres}")
        
        return {
            "profile_id": profile_id,
            "profile": user_profile
        }
        
    except Exception as e:
        end_time = time.time()
        logger.error(f"❌ PROFILE CREATION ERROR after {end_time - start_time:.2f}s")
        logger.error(f"❌ Error details: {str(e)}")
        logger.exception("Full error traceback:")
        
        return {"error": f"Erreur lors de la création du profil: {str(e)}"}

@app.post("/recommendations/from-profile")
def get_recommendations_from_profile(request: ProfileRecommendationRequest):
    """
    Génère des recommandations basées sur un profil utilisateur existant
    
    Args:
        request: Requête contenant le profil utilisateur et une requête personnalisée optionnelle
    
    Returns:
        Recommandations de films personnalisées basées sur le profil
    """
    logger.info(f"🎯 API CALL - /recommendations/from-profile")
    logger.info(f"🎬 Profile genres: {request.profile.favorite_genres}")
    logger.info(f"💭 Custom query: {request.custom_query}")
    
    start_time = time.time()
    
    try:
        logger.info(f"🚀 Starting profile-based recommendation process...")

        recommendations = movie_recommender.get_recommendations_from_profile(request.profile,request.custom_query)
        end_time = time.time()
        logger.info(f"⏱️ Profile-based Recommendation Time: {end_time - start_time:.2f}s")
        logger.info(f"✅ PROFILE-BASED RECOMMENDATIONS SUCCESS")
        
        return recommendations
        
    except Exception as e:
        end_time = time.time()
        logger.error(f"❌ PROFILE-BASED RECOMMENDATIONS ERROR after {end_time - start_time:.2f}s")
        logger.error(f"❌ Error details: {str(e)}")
        logger.exception("Full error traceback:")
        
        return {"error": f"Erreur lors de la génération des recommandations basées sur le profil: {str(e)}"}

@app.get("/profile/list")
def list_profiles(http_request: Request):
    """
    Liste tous les profils de la session courante
    
    Args:
        http_request: Requête HTTP pour la gestion de session
    
    Returns:
        Liste des profils avec leurs IDs
    """
    logger.info(f"📋 API CALL - /profile/list")
    
    try:
        # Use get_or_create_session_id to handle cases where no session exists
        session_id = get_or_create_session_id(http_request)
        
        # Get all profiles for this session
        session_profiles = profile_service.get_session_profiles(session_id)
        
        # Convert to list format with profile_id and profile data
        profiles_list = [
            {
                "profile_id": profile_id,
                "profile": profile
            }
            for profile_id, profile in session_profiles.items()
        ]
        
        logger.info(f"✅ Found {len(profiles_list)} profiles in session {session_id}")
        
        return {"profiles": profiles_list}
        
    except Exception as e:
        logger.error(f"❌ LIST PROFILES ERROR: {str(e)}")
        logger.exception("Full error traceback:")
        return {"profiles": []}

@app.get("/profile/{profile_id}")
def get_profile(profile_id: str, http_request: Request):
    """
    Récupère un profil spécifique par son ID
    
    Args:
        profile_id: Identifiant du profil
        http_request: Requête HTTP pour la gestion de session
    
    Returns:
        Profile: Le profil demandé
    """
    logger.info(f"👤 API CALL - /profile/{profile_id}")
    
    try:
        # Récupérer la session
        session_id = get_session_id(http_request)
        
        # Récupérer le profil
        profile = profile_service.get_profile(session_id, profile_id)
        
        if not profile:
            logger.warning(f"❌ Profile not found: {profile_id} in session {session_id}")
            raise HTTPException(status_code=404, detail="Profile not found")
        
        logger.info(f"✅ Profile retrieved successfully: {profile_id}")
        return profile
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ GET PROFILE ERROR: {str(e)}")
        logger.exception("Full error traceback:")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération du profil: {str(e)}")

@app.put("/profile/{profile_id}")
def update_profile(profile_id: str, updated_profile: Profile, http_request: Request):
    """
    Met à jour un profil existant
    
    Args:
        profile_id: Identifiant du profil
        updated_profile: Profil mis à jour
        http_request: Requête HTTP pour la gestion de session
    
    Returns:
        Dict contenant le profil mis à jour
    """
    logger.info(f"✏️ API CALL - /profile/{profile_id} UPDATE")
    logger.debug(f"📝 Updated genres: {updated_profile.favorite_genres}")
    print(updated_profile)
    start_time = time.time()
    
    try:
        # Récupérer la session
        print("getting session id")
        session_id = get_or_create_session_id(http_request)
        print("session id recupéré ")
        
        # Vérifier que le profil existe
        existing_profile = profile_service.get_profile(session_id, profile_id)
        if not existing_profile:
            logger.warning(f"❌ Profile not found for update: {profile_id} in session {session_id}")
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Sauvegarder le profil mis à jour
        profile_service.save_profile(session_id, profile_id, updated_profile)
        
        end_time = time.time()
        logger.info(f"⏱️ Profile Update Time: {end_time - start_time:.2f}s")
        logger.info(f"✅ PROFILE UPDATE SUCCESS")
        logger.info(f"🆔 Profile ID: {profile_id}")
        logger.info(f"🔗 Session ID: {session_id}")
        
        return {
            "success": True,
            "profile_id": profile_id,
            "profile": updated_profile
        }
        
    except HTTPException:
        raise
    except Exception as e:
        end_time = time.time()
        logger.error(f"❌ PROFILE UPDATE ERROR after {end_time - start_time:.2f}s")
        logger.error(f"❌ Error details: {str(e)}")
        logger.exception("Full error traceback:")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour du profil: {str(e)}")

@app.get("/debug/sessions")
def debug_sessions():
    """
    Endpoint de debug pour voir les sessions actives (à supprimer en production)
    
    Returns:
        Informations sur les sessions
    """
    return {
        "total_sessions": profile_service.get_session_count(),
        "total_profiles": profile_service.get_total_profiles_count()
    }
