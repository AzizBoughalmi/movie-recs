from math import inf
from pydantic_ai import Agent
import requests
from dotenv import load_dotenv
#import nest_asyncio
import os
import time
from pydantic import BaseModel
from typing import List, Any
from utils.retry_handler import retry_on_429
from utils.rate_limiter import rate_limit

load_dotenv()


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

@rate_limit(min_interval=2.0)
@retry_on_429(max_retries=5, base_delay=1.0, max_delay=30.0, jitter=True)
def search_movies_langsearch(query: str, count: int = 5, freshness: str = "noLimit", summary: bool = True):
    """
    use this tool to search for informations about movies, actors , producers , themes .

    """
    print(f"🔍 TOOL CALL - LangSearch: query='{query}', count={count}")
    
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
    
    start_time = time.time()
    resp = requests.post(LANGSEARCH_ENDPOINT, headers=headers, json=payload, timeout=15)
    end_time = time.time()
    
    resp.raise_for_status()
    data = resp.json()

    results = data.get("data", {}).get("webPages", {}).get("value", [])
    processed = []
    for item in results:
        processed.append({
            "title": item.get("name"),
            "url": item.get("url"),
            "snippet": item.get("snippet"),
            "summary": item.get("summary")
        })
    
    print(f"✅ TOOL RESULT - LangSearch: Found {len(processed)} items")
    
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
                return full_poster_url
            
    except Exception as e:
        pass
    
    return ""

def load_system_prompt() -> str:
    """
    Charge le prompt système depuis le fichier markdown
    
    Returns:
        str: Le contenu du prompt système
    """
    try:
        prompt_path = os.path.join(os.path.dirname(__file__), "system_prompt_simplified.md")
        with open(prompt_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except Exception as e:
        # Fallback vers le prompt hardcodé en cas d'erreur
        fallback_prompt = """Tu es un assistant de cinéma qui suggère des films basés sur les préférences de l'utilisateur. 

Pour chaque suggestion de film, tu expliques pourquoi tu le suggères. Tu donneras au moins 3 suggestions. 
Utilise les informations trouvées via l'outil de recherche pour enrichir tes recommandations."""
        return fallback_prompt

def convert_agent_movies_to_movies(agent_movies: AgentMovies) -> Movies:
    """
    Convertit les films de l'agent en films enrichis avec les posters TMDB
    
    Args:
        agent_movies: Résultats de l'agent sans posters
    
    Returns:
        Movies: Films enrichis avec les posters TMDB
    """
    enriched_movies = []
    
    for agent_movie in agent_movies.movies:
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
    # Charger le prompt système depuis le fichier markdown
    system_prompt = load_system_prompt()
    
    # Créer l'agent avec le prompt personnalisé
    agent = Agent(
        'gemini-2.0-flash',
        output_type=AgentMovies,
        tools=[search_movies_langsearch],
        system_prompt=system_prompt,
    )
    
    # Construire la requête
    if query:
        user_query = f"Voici les films que j'aime : {', '.join(liked_movies)}. {query}"
    else:
        user_query = f"Voici les films que j'aime : {', '.join(liked_movies)}. Peux-tu me suggérer des films similaires ?"
    
    # Lancer l'agent et récupérer les résultats
    start_time = time.time()
    result = agent.run_sync(user_query)
    end_time = time.time()
     
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
