from pydantic_ai import Agent
import requests
from dotenv import load_dotenv
import nest_asyncio
import os
import logging
import time
from pydantic import BaseModel
from typing import List, Any
from utils.search_tools import search_movies_langsearch
from backend.app.profiler_test import Profile


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
nest_asyncio.apply()

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

def get_movie_recommendations_from_profile(user_profile: Profile, query: str | None = None) -> Movies:
    """
    Fonction qui prend un profil utilisateur et retourne des recommandations de films personnalisées.
    
    Args:
        user_profile: Profil cinématographique de l'utilisateur
        query: Requête optionnelle pour personnaliser la recherche
    
    Returns:
        Movies: Résultat de l'agent contenant la liste des films recommandés avec posters
    """
    logger.info(f"🎬 STARTING PROFILE-BASED RECOMMENDATION PROCESS")

    logger.info(f"🎭 Favorite genres: {user_profile.favorite_genres}")
    logger.info(f"🎬 Favorite directors: {user_profile.favorite_directors}")
    logger.info(f"💭 Custom query: {query}")
    
    # Créer l'agent avec un prompt spécialisé pour les profils utilisateur
    agent = Agent(
        'gemini-2.0-flash',
        output_type=AgentMovies,
        tools=[search_movies_langsearch],
        system_prompt="""Tu es un expert en recommandations cinématographiques personnalisées. Tu analyses le profil détaillé d'un utilisateur pour suggérer des films parfaitement adaptés à ses goûts.

Tu utilises toutes les informations du profil utilisateur :
- Genres préférés et à explorer
- Réalisateurs et acteurs favoris
- Décennies préférées
- Traits de personnalité cinématographique
- Préférences d'ambiance de visionnage
- Description du goût cinématographique

Pour chaque recommandation, tu expliques précisément pourquoi ce film correspond au profil de l'utilisateur.
Tu donneras au moins 5 suggestions variées mais cohérentes avec le profil.
Utilise l'outil de recherche si nécessaire pour enrichir tes recommandations avec des informations actualisées."""
    )
    
    # Construire la requête basée sur le profil
    profile_summary = f"""
Profil de {user_profile.user_name} :
- Genres favoris : {', '.join(user_profile.favorite_genres) if user_profile.favorite_genres else 'Non spécifiés'}
- Réalisateurs favoris : {', '.join(user_profile.favorite_directors) if user_profile.favorite_directors else 'Non spécifiés'}
- Acteurs favoris : {', '.join(user_profile.favorite_actors) if user_profile.favorite_actors else 'Non spécifiés'}
- Décennies préférées : {', '.join(user_profile.preferred_decades) if user_profile.preferred_decades else 'Non spécifiées'}
- Préférences cinématographiques : {user_profile.movie_preferences}
- Traits de personnalité : {user_profile.personality_traits}
- Description du goût : {user_profile.cinematic_taste_description}
- Genres à explorer : {', '.join(user_profile.recommended_genres_to_explore) if user_profile.recommended_genres_to_explore else 'Non spécifiés'}
- Préférences d'ambiance : {', '.join(user_profile.viewing_mood_preferences) if user_profile.viewing_mood_preferences else 'Non spécifiées'}
"""
    
    if query:
        user_query = f"{profile_summary}\n\nRequête spécifique : {query}\n\nBasé sur ce profil détaillé, recommande des films parfaitement adaptés."
    else:
        user_query = f"{profile_summary}\n\nBasé sur ce profil cinématographique détaillé, recommande des films qui correspondent parfaitement aux goûts et à la personnalité de cet utilisateur."
    
    logger.info(f"🤖 Sending profile-based query to Gemini AI")
    logger.debug(f"📝 Profile summary: {profile_summary[:200]}...")
    
    # Lancer l'agent et récupérer les résultats
    start_time = time.time()
    result = agent.run_sync(user_query)
    end_time = time.time()
    
    logger.info(f"⏱️ Total AI Processing Time: {end_time - start_time:.2f}s")
    logger.info(f"✅ AGENT COMPLETE - Generated {len(result.output.movies)} profile-based recommendations")
    
    # Log des recommandations de l'agent
    for i, movie in enumerate(result.output.movies, 1):
        logger.debug(f"  {i}. {movie.title} ({movie.year}) - {movie.genre}")
        logger.debug(f"     Why: {movie.why_recommended[:100]}...")
    
    # Convertir et enrichir avec les posters TMDB
    return convert_agent_movies_to_movies(result.output)

# Fonction de compatibilité (garde l'ancienne fonction pour la rétrocompatibilité)
def get_movie_recommendations(liked_movies: list[str], query: str | None = None) -> Movies:
    """
    Fonction de compatibilité - utilise l'ancienne méthode basée sur une liste de films.
    DEPRECATED: Utilisez get_movie_recommendations_from_profile() à la place.
    """
    logger.warning("⚠️ DEPRECATED: get_movie_recommendations() is deprecated. Use get_movie_recommendations_from_profile() instead.")
    
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
    
    logger.info(f"⏱️ Total AI Processing Time: {end_time - start_time:.2f}s")
    logger.info(f"✅ AGENT COMPLETE - Generated {len(result.output.movies)} recommendations")
    
    # Convertir et enrichir avec les posters TMDB
    return convert_agent_movies_to_movies(result.output)

# Exemple d'utilisation
if __name__ == "__main__":
    from backend.app.profiler_test import create_user_profile
    
    print("🎬 DÉMONSTRATION DE L'INTÉGRATION PROFILE_MAKER + RECOMMENDER_AGENT")
    print("=" * 70)
    
    # Étape 1: Créer un profil utilisateur à partir de films favoris
    print("\n📝 ÉTAPE 1: Création du profil utilisateur")
    favorite_movies = ["The Godfather", "Pulp Fiction", "The Dark Knight"]
   
    
    print(f"Films favoris de {user_name}: {', '.join(favorite_movies)}")
    print("🔄 Création du profil en cours...")
    
    try:
        user_profile = create_user_profile(favorite_movies, user_name)
        print("✅ Profil créé avec succès!")
        
        # Afficher un résumé du profil
        print(f"\n👤 PROFIL DE {user_profile.user_name.upper()}:")
        print(f"🎭 Genres favoris: {', '.join(user_profile.favorite_genres[:3])}{'...' if len(user_profile.favorite_genres) > 3 else ''}")
        print(f"🎬 Réalisateurs favoris: {', '.join(user_profile.favorite_directors[:2])}{'...' if len(user_profile.favorite_directors) > 2 else ''}")
        print(f"💭 Traits: {user_profile.personality_traits[:100]}...")
        
        # Étape 2: Générer des recommandations basées sur le profil
        print(f"\n🎯 ÉTAPE 2: Génération de recommandations personnalisées")
        print("🔄 Analyse du profil et recherche de films adaptés...")
        
        recommendations = get_movie_recommendations_from_profile(user_profile)
        
        print(f"✅ {len(recommendations.movies)} recommandations générées!")
        
        # Afficher les résultats
        print(f"\n🎬 FILMS RECOMMANDÉS POUR {user_profile.user_name.upper()}:")
        print("=" * 50)
        
        for i, movie in enumerate(recommendations.movies, 1):
            print(f"\n{i}. 🎭 {movie.title} ({movie.year})")
            print(f"   📂 Genre: {movie.genre}")
            if movie.director:
                print(f"   🎬 Réalisateur: {movie.director}")
            print(f"   💡 Pourquoi recommandé: {movie.why_recommended}")
            if movie.cast:
                print(f"   ⭐ Cast: {', '.join(movie.cast[:3])}{'...' if len(movie.cast) > 3 else ''}")
            if movie.poster_path:
                print(f"   🖼️ Poster: ✅")
            print("   " + "-" * 40)
        
        print(f"\n🎉 DÉMONSTRATION TERMINÉE AVEC SUCCÈS!")
        print("✅ Le système profile_maker + recommender_agent fonctionne parfaitement!")
        
    except Exception as e:
        print(f"❌ Erreur lors de la démonstration: {str(e)}")
        print("\n🔄 Utilisation de l'ancienne méthode comme fallback...")
        
        # Fallback vers l'ancienne méthode
        recommendations = get_movie_recommendations(favorite_movies)
        
        print("Films recommandés (méthode classique):")
        for movie in recommendations.movies:
            print(f"\n- {movie.title} ({movie.year})")
            print(f"  Genre: {movie.genre}")
            print(f"  Réalisateur: {movie.director}")
            print(f"  Pourquoi recommandé: {movie.why_recommended}")
