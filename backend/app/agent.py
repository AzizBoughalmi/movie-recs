from pydantic_ai import Agent
import requests
from dotenv import load_dotenv
#import nest_asyncio
import os
import logging
import time
from pydantic import BaseModel
from typing import List, Any

load_dotenv()

# Configuration du logging pour le debugging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
LOG_TO_FILE = os.getenv('LOG_TO_FILE', 'false').lower() == 'true'

handlers = [logging.StreamHandler()]
if LOG_TO_FILE:
    handlers.append(logging.FileHandler('agent.log'))

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=handlers
)
logger = logging.getLogger(__name__)

logger.info(f"🔧 Logging configured: Level={LOG_LEVEL}, File={LOG_TO_FILE}")
#nest_asyncio.apply()

api_key = os.getenv('GEMINI_API_KEY')
LANGSEARCH_ENDPOINT = "https://api.langsearch.com/v1/web-search"
LANGSEARCH_API_KEY = os.getenv("LANGSEARCH_API_KEY")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"

# Classe pour l'output de l'agent (sans poster_path)
class AgentMovie(BaseModel):
    title: str
    year: str = ""
    genre: str = ""
    director: str = ""
    description: str = ""
    why_recommended: str
    rating: str = ""
    cast: list[str] = []

class AgentMovies(BaseModel):
    movies: list[AgentMovie]

# Classe finale avec poster_path (après enrichissement TMDB)
class Movie(BaseModel):
    title: str
    year: str = ""
    genre: str = ""
    director: str = ""
    description: str = ""
    why_recommended: str
    rating: str = ""
    cast: list[str] = []
    poster_path: str = ""

class Movies(BaseModel):
    movies: list[Movie]

def search_movies_langsearch(query: str, count: int = 5, freshness: str = "noLimit", summary: bool = True):
    """
    use this tool to search for movies similar to a given title ; or for movies of a spcific genre , or for actors in movies.
    use this tool once to find infomation about the given movie. the use this tool again to find movies similar to the given movie using the information extracted at the beginning
    """
    logger.info(f"🔍 TOOL CALL - LangSearch: query='{query}', count={count}")
    
    headers = {
        "Authorization": f"Bearer {LANGSEARCH_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "query": query,
        "freshness": freshness,
        "summary": summary,
        "count": count
    }
    
    logger.debug(f"📤 LangSearch Request: {LANGSEARCH_ENDPOINT}")
    logger.debug(f"📤 Payload: {payload}")
    
    start_time = time.time()
    resp = requests.post(LANGSEARCH_ENDPOINT, headers=headers, json=payload, timeout=15)
    end_time = time.time()
    
    logger.info(f"⏱️ LangSearch Response Time: {end_time - start_time:.2f}s")
    logger.debug(f"📥 Status Code: {resp.status_code}")
    
    resp.raise_for_status()
    data = resp.json()
    
    logger.debug(f"📥 Raw Response Keys: {list(data.keys())}")

    results = data.get("data", {}).get("webPages", {}).get("value", [])
    processed = []
    for item in results:
        processed.append({
            "title": item.get("name"),
            "url": item.get("url"),
            "snippet": item.get("snippet"),
            "summary": item.get("summary")
        })
    
    logger.info(f"✅ LangSearch Results: Found {len(processed)} items")
    for i, item in enumerate(processed[:3]):  # Log first 3 results
        logger.debug(f"  {i+1}. {item.get('title', 'No title')}")
    
    return processed

def search_movie_poster_tmdb(title: str, year: str = "") -> str:
    """
    Recherche le poster d'un film via l'API TMDB
    
    Args:
        title: Titre du film
        year: Année du film (optionnel)
    
    Returns:
        str: URL complète du poster ou chaîne vide si non trouvé
    """
    logger.info(f"🎬 TMDB POSTER SEARCH: '{title}' ({year})")
    
    try:
        # Recherche du film sur TMDB
        search_url = f"{TMDB_BASE_URL}/search/movie"
        params = {
            "api_key": TMDB_API_KEY,
            "query": title,
            "language": "fr-FR"
        }
        
        if year:
            params["year"] = year
        
        logger.debug(f"📤 TMDB Search Request: {search_url}")
        logger.debug(f"📤 Params: {params}")
        
        response = requests.get(search_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        results = data.get("results", [])
        
        if results:
            # Prendre le premier résultat
            movie = results[0]
            poster_path = movie.get("poster_path")
            
            if poster_path:
                full_poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                logger.info(f"✅ TMDB Poster found: {full_poster_url}")
                return full_poster_url
            else:
                logger.info(f"⚠️ TMDB: No poster found for '{title}'")
        else:
            logger.info(f"⚠️ TMDB: No results found for '{title}'")
            
    except Exception as e:
        logger.error(f"❌ TMDB Error for '{title}': {str(e)}")
    
    return ""

def convert_agent_movies_to_movies(agent_movies: AgentMovies) -> Movies:
    """
    Convertit les films de l'agent en films enrichis avec les posters TMDB
    
    Args:
        agent_movies: Résultats de l'agent sans posters
    
    Returns:
        Movies: Films enrichis avec les posters TMDB
    """
    logger.info(f"🎨 ENRICHING {len(agent_movies.movies)} MOVIES WITH TMDB POSTERS")
    enriched_movies = []
    
    for agent_movie in agent_movies.movies:
        logger.info(f"🔍 Searching poster for: {agent_movie.title} ({agent_movie.year})")
        poster_url = search_movie_poster_tmdb(agent_movie.title, agent_movie.year)
        
        # Créer un nouveau film avec le poster
        enriched_movie = Movie(
            title=agent_movie.title,
            year=agent_movie.year,
            genre=agent_movie.genre,
            director=agent_movie.director,
            description=agent_movie.description,
            why_recommended=agent_movie.why_recommended,
            rating=agent_movie.rating,
            cast=agent_movie.cast,
            poster_path=poster_url
        )
        enriched_movies.append(enriched_movie)
    
    logger.info(f"✅ ENRICHMENT COMPLETE - {len(enriched_movies)} movies with posters")
    
    # Log des films enrichis
    for i, movie in enumerate(enriched_movies, 1):
        logger.debug(f"  {i}. {movie.title} ({movie.year}) - {movie.genre}")
        logger.debug(f"     Poster: {'✅' if movie.poster_path else '❌'}")
    
    return Movies(movies=enriched_movies)

def get_movie_recommendations(liked_movies: list[str], query: str | None = None) -> Movies:
    """
    Fonction qui prend une liste de films aimés et retourne des recommandations de films similaires.
    
    Args:
        liked_movies: Liste des titres de films que l'utilisateur aime
        query: Requête optionnelle pour personnaliser la recherche
    
    Returns:
        Any: Résultat de l'agent contenant la liste des films recommandés
    """
    logger.info(f"🎬 STARTING RECOMMENDATION PROCESS")
    logger.info(f"📝 User's favorite movies: {liked_movies}")
    logger.info(f"💭 Custom query: {query}")
    
    # Créer l'agent avec le prompt personnalisé
    agent = Agent(
        'gemini-2.0-flash',
        output_type=AgentMovies,
        tools=[search_movies_langsearch],
        system_prompt="""Tu es un assistant de cinéma qui suggère des films basés sur les préférences de l'utilisateur. 

Pour chaque suggestion de film, tu expliques pourquoi tu le suggères. Tu donneras au moins 3 suggestions. 
Utilise les informations trouvées via l'outil de recherche pour enrichir tes recommandations."""
    )
    
    # Construire la requête
    if query:
        user_query = f"Voici les films que j'aime : {', '.join(liked_movies)}. {query}"
    else:
        user_query = f"Voici les films que j'aime : {', '.join(liked_movies)}. Peux-tu me suggérer des films similaires ?"
    
    logger.info(f"🤖 Sending query to Gemini AI: '{user_query}'")
    
    # Lancer l'agent et récupérer les résultats
    start_time = time.time()
    result = agent.run_sync(user_query)
    end_time = time.time()
    print(result)
    logger.info(f"⏱️ Total AI Processing Time: {end_time - start_time:.2f}s")
    logger.info(f"✅ AGENT COMPLETE - Generated {len(result.output.movies)} recommendations")
    
    # Log des recommandations de l'agent
    for i, movie in enumerate(result.output.movies, 1):
        logger.debug(f"  {i}. {movie.title} ({movie.year}) - {movie.genre}")
        logger.debug(f"     Why: {movie.why_recommended[:100]}...")
    
    # Convertir et enrichir avec les posters TMDB
    return convert_agent_movies_to_movies(result.output)

# Exemple d'utilisation
if __name__ == "__main__":
    # Liste de films que l'utilisateur aime
    liked_movies = ["The Godfather", "Spider-Man"]
    
    # Obtenir des recommandations
    recommendations = get_movie_recommendations(liked_movies)
    
    # Afficher les résultats
    print("Films recommandés :")
    for movie in recommendations.movies:
        print(f"\n- {movie.title} ({movie.year})")
        print(f"  Genre: {movie.genre}")
        print(f"  Réalisateur: {movie.director}")
        print(f"  Pourquoi recommandé: {movie.why_recommended}")
        if movie.cast:
            print(f"  Cast: {', '.join(movie.cast)}")
