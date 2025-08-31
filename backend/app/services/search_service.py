import requests
import time
from threading import Lock
from functools import wraps
from typing import List, Dict, Any, Callable
import logging
from config.settings import settings

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Rate limiter pour contrôler la fréquence des appels à une API
    """
    
    def __init__(self, min_interval: float = 2.0):
        """
        Initialise le rate limiter
        
        Args:
            min_interval: Intervalle minimum en secondes entre les appels
        """
        self.min_interval = min_interval
        self.last_call_time = 0
        self.lock = Lock()
    
    def wait_if_needed(self) -> float:
        """
        Attend si nécessaire pour respecter l'intervalle minimum
        
        Returns:
            float: Temps d'attente effectif en secondes
        """
        with self.lock:
            current_time = time.time()
            time_since_last = current_time - self.last_call_time
            
            if time_since_last < self.min_interval:
                sleep_time = self.min_interval - time_since_last
                logger.info(f"Rate limiting: attente de {sleep_time:.2f}s")
                print(f"⏱️ Rate limiting: attente de {sleep_time:.2f}s avant prochain appel")
                time.sleep(sleep_time)
                self.last_call_time = time.time()
                return sleep_time
            else:
                self.last_call_time = current_time
                return 0.0

def rate_limit(min_interval: float = 2.0):
    """
    Décorateur pour appliquer un rate limiting à une fonction
    
    Args:
        min_interval: Intervalle minimum en secondes entre les appels
    """
    # Créer une instance de rate limiter pour cette fonction
    limiter = RateLimiter(min_interval)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Attendre si nécessaire
            wait_time = limiter.wait_if_needed()
            
            if wait_time > 0:
                logger.debug(f"Rate limiter a attendu {wait_time:.2f}s pour {func.__name__}")
            
            # Exécuter la fonction
            return func(*args, **kwargs)
            
        return wrapper
    return decorator

# Instance globale pour LangSearch
langsearch_limiter = RateLimiter(min_interval=3.0)

class SearchService:
    """Service pour les recherches via LangSearch API"""
    
    def __init__(self):
        self.endpoint = settings.LANGSEARCH_ENDPOINT
        self.api_key = settings.LANGSEARCH_API_KEY
    
    @rate_limit(2.0)
    def search_movies(self, query: str, count: int | None = None, freshness: str | None = None, summary: bool = True) -> List[Dict[str, Any]]|str:
        """
        Recherche des informations sur les films et le cinéma
        
        Args:
            query: Requête de recherche
            count: Nombre de résultats à retourner
            freshness: Fraîcheur des résultats ("noLimit", "day", "week", "month")
            summary: Inclure un résumé des résultats
        
        Returns:
            List[Dict]: Liste des résultats de recherche avec titre, URL, snippet et résumé
        """
        #debug
        print("query : " + query)
        if count is None:
            count = settings.DEFAULT_SEARCH_COUNT
        if freshness is None:
            freshness = settings.DEFAULT_SEARCH_FRESHNESS
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": query,
            "freshness": freshness,
            "summary": summary,
            "count": count
        }
        try:
            response = requests.post(
                self.endpoint, 
                headers=headers, 
                json=payload, 
                timeout=settings.API_TIMEOUT
            )
            response.raise_for_status()
            
            data = response.json()
            results = data.get("data", {}).get("webPages", {}).get("value", [])
            
            processed = []
            for item in results:
                processed.append({
                    "title": item.get("name"),
                    "url": item.get("url"),
                    "snippet": item.get("snippet"),
                    "summary": item.get("summary")
                })
                #debug
                print("result: " + item.get("name"))
            
            return processed
        except :
            return "Error : try again later"

# Instance globale du service
search_service = SearchService()

# Fonction pour compatibilité avec l'ancien code
def search_movies_langsearch(query: str, count: int = 5, freshness: str = "noLimit", summary: bool = True):
    """Fonction de compatibilité pour l'ancien code"""
    return search_service.search_movies(query, count, freshness, summary)
