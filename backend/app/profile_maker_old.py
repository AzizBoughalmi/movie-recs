from pydantic_ai import Agent
from dotenv import load_dotenv
import os
import logging
import time
import nest_asyncio
from pydantic import BaseModel
from typing import List, Any
from utils.search_tools import search_movies_langsearch

load_dotenv()
nest_asyncio.apply()
# Configuration du logging
logger = logging.getLogger(__name__)

# Variables d'environnement
api_key = os.getenv('GEMINI_API_KEY')

# Classe pour le profil utilisateur (output de l'agent profile_maker)
class Profile(BaseModel):
    favorite_genres: list[str] = []
    favorite_directors: list[str] = []
    favorite_actors: list[str] = []
    preferred_decades: list[str] = []
    movie_preferences: str = ""
    personality_traits: str = ""
    cinematic_taste_description: str = ""
    recommended_genres_to_explore: list[str] = []
    viewing_mood_preferences: list[str] = []


def create_user_profile(favorite_movies: list[str]) -> Profile:
    """
    Fonction qui analyse les films favoris de l'utilisateur pour créer un profil cinématographique détaillé.
    
    Args:
        favorite_movies: Liste des titres de films favoris de l'utilisateur
        user_name: Nom de l'utilisateur (optionnel)
    
    Returns:
        Profile: Profil cinématographique détaillé de l'utilisateur
    """
    logger.info(f"🎭 STARTING PROFILE CREATION PROCESS")
    logger.info(f"👤 User: {user_name}")
    logger.info(f"🎬 Favorite movies: {favorite_movies}")
    
    # Créer l'agent profile_maker avec un prompt spécialisé
    profile_agent = Agent(
        'gemini-2.0-flash',
        output_type=Profile,
        tools=[search_movies_langsearch],
        system_prompt="""Tu es un expert en cinématographie et en analyse psychologique des goûts cinématographiques. 
        
        Ton rôle est d'analyser les films favoris d'un utilisateur pour créer un profil détaillé de ses préférences et de sa personnalité cinématographique.
        
        Pour chaque analyse, tu dois :
        1. Identifier les genres, réalisateurs, acteurs récurrents dans ses choix
        2. Analyser les décennies/époques préférées
        3. Comprendre les thèmes et motifs qui l'attirent
        4. Déduire des traits de personnalité basés sur ses choix cinématographiques
        5. Créer une description narrative de son goût cinématographique
        6. Suggérer de nouveaux genres à explorer
        7. Identifier ses préférences d'ambiance de visionnage
        
        N'Utiliser l'outil de recherche que dans le cas où un film est inconnu pour toi .
        
        Sois précis, perspicace et créatif dans ton analyse. Crée un profil riche et nuancé qui capture vraiment l'essence des goûts cinématographiques de l'utilisateur."""
    )
    
    # Construire la requête d'analyse
    user_query = f"""Analyse les films favoris de {user_name} pour créer son profil cinématographique : {', '.join(favorite_movies)}.
    
    Crée un profil détaillé qui inclut :
    - Les genres préférés
    - Les réalisateurs et acteurs favoris
    - Les décennies/époques préférées
    - Une analyse de ses préférences cinématographiques
    - Des traits de personnalité déduits de ses choix
    - Une description narrative de son goût cinématographique
    - Des genres recommandés à explorer
    - Ses préférences d'ambiance de visionnage
    
    """
    
    logger.info(f"🤖 Sending analysis query to Gemini AI")
    
    # Lancer l'agent et récupérer le profil
    start_time = time.time()
    result = profile_agent.run_sync(user_query)
    end_time = time.time()
    
    logger.info(f"⏱️ Total Profile Creation Time: {end_time - start_time:.2f}s")
    logger.info(f"✅ PROFILE CREATION COMPLETE")
    
    # Log du profil créé
    profile = result.output
    logger.debug(f"👤 Profile for: {profile.user_name}")
    logger.debug(f"🎭 Favorite genres: {profile.favorite_genres}")
    logger.debug(f"🎬 Favorite directors: {profile.favorite_directors}")
    logger.debug(f"⭐ Favorite actors: {profile.favorite_actors}")
    logger.debug(f"📅 Preferred decades: {profile.preferred_decades}")
    logger.debug(f"💭 Personality traits: {profile.personality_traits[:100]}...")
    
    return profile

# Exemple d'utilisation
if __name__ == "__main__":
    # Films favoris de l'utilisateur
    favorite_movies = [ " في عِزّ الظهر"]
 
    
    # Créer le profil utilisateur
    user_profile = create_user_profile(favorite_movies, user_name)
    
    # Afficher le profil
    print(f"\n🎭 PROFIL CINÉMATOGRAPHIQUE DE {user_profile.user_name.upper()}")
    print("=" * 50)
    
    print(f"\n🎬 Genres favoris: {', '.join(user_profile.favorite_genres)}")
    print(f"🎥 Réalisateurs favoris: {', '.join(user_profile.favorite_directors)}")
    print(f"⭐ Acteurs favoris: {', '.join(user_profile.favorite_actors)}")
    print(f"📅 Décennies préférées: {', '.join(user_profile.preferred_decades)}")
    
    print(f"\n💭 Préférences cinématographiques:")
    print(user_profile.movie_preferences)
    
    print(f"\n🧠 Traits de personnalité:")
    print(user_profile.personality_traits)
    
    print(f"\n🎨 Description du goût cinématographique:")
    print(user_profile.cinematic_taste_description)
    
    print(f"\n🔍 Genres recommandés à explorer: {', '.join(user_profile.recommended_genres_to_explore)}")
    print(f"🌙 Préférences d'ambiance: {', '.join(user_profile.viewing_mood_preferences)}")
