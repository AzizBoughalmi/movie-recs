import requests
from app.config.settings import settings

class TMDBService:
    """Service pour les interactions avec l'API TMDB"""
    
    def __init__(self):
        self.api_key = settings.TMDB_API_KEY
        self.base_url = settings.TMDB_BASE_URL
        self.image_base_url = settings.TMDB_IMAGE_BASE_URL
    
    def search_movie_poster(self, title: str, year: str = "") -> str:
        """
        Recherche le poster d'un film via l'API TMDB
        
        Args:
            title: Titre du film
            year: Année du film (optionnel)
        
        Returns:
            str: URL complète du poster ou chaîne vide si non trouvé
        """
        try:
            search_url = f"{self.base_url}/search/movie"
            params = {
                "api_key": self.api_key,
                "query": title,
                "language": "fr-FR"
            }
            
            if year:
                params["year"] = year
            
            response = requests.get(search_url, params=params, timeout=settings.API_TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", [])
            
            if results:
                movie = results[0]
                poster_path = movie.get("poster_path")
                
                if poster_path:
                    return f"{self.image_base_url}{poster_path}"
            
        except Exception:
            # En cas d'erreur, retourner une chaîne vide
            pass
        
        return ""

# Instance globale du service
tmdb_service = TMDBService()
