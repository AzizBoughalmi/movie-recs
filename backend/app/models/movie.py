from pydantic import BaseModel
from typing import List

class AgentMovie(BaseModel):
    """Modèle pour les films retournés par l'agent AI (sans poster)"""
    title: str
    year: str = ""
    genre: str = ""
    director: str = ""
    description: str = ""
    why_recommended: str
    rating: str = ""
    cast: List[str] = []

class AgentMovies(BaseModel):
    """Collection de films retournés par l'agent AI"""
    movies: List[AgentMovie]

class Movie(BaseModel):
    """Modèle final pour les films avec poster TMDB"""
    title: str
    year: str = ""
    genre: str = ""
    director: str = ""
    description: str = ""
    why_recommended: str
    rating: str = ""
    cast: List[str] = []
    poster_path: str = ""

class Movies(BaseModel):
    """Collection de films enrichis avec posters"""
    movies: List[Movie]
