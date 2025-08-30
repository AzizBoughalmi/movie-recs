import requests
from typing import List, Dict, Any
from config.settings import settings

class SearchService:
    """Service pour les recherches via LangSearch API"""
    
    def __init__(self):
        self.endpoint = settings.LANGSEARCH_ENDPOINT
        self.api_key = settings.LANGSEARCH_API_KEY
    
    def search_movies(self, query: str, count: int | None = None, freshness: str | None = None, summary: bool = True) -> List[Dict[str, Any]]:
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
        
        return processed

# Instance globale du service
search_service = SearchService()

# Fonction pour compatibilité avec l'ancien code
def search_movies_langsearch(query: str, count: int = 5, freshness: str = "noLimit", summary: bool = True):
    """Fonction de compatibilité pour l'ancien code"""
    return search_service.search_movies(query, count, freshness, summary)
