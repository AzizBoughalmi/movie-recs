from pydantic import BaseModel
from typing import List

class Profile(BaseModel):
    """Modèle pour le profil cinématographique d'un utilisateur"""
    favorite_genres: List[str] 
    favorite_directors: List[str] 
    favorite_actors: List[str] 
    preferred_decades: List[str] 
    movies_watched: List[str]
    movie_preferences: str 
    personality_traits: str 
    cinematic_taste_description: str 
    recommended_genres_to_explore: List[str]
    viewing_mood_preferences: List[str] 