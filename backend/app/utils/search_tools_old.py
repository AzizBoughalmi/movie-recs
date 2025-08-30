import requests
import logging
import time
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration du logging
logger = logging.getLogger(__name__)

# Variables d'environnement
LANGSEARCH_ENDPOINT = "https://api.langsearch.com/v1/web-search"
LANGSEARCH_API_KEY = os.getenv("LANGSEARCH_API_KEY")

def search_movies_langsearch(query: str, count: int = 5, freshness: str = "noLimit", summary: bool = True):
    """
    Outil pour rechercher des informations sur les films et le cinéma.
    Utilisé par les agents pour enrichir leurs analyses avec des données externes.
    
    Args:
        query: Requête de recherche
        count: Nombre de résultats à retourner
        freshness: Fraîcheur des résultats ("noLimit", "day", "week", "month")
        summary: Inclure un résumé des résultats
    
    Returns:
        list: Liste des résultats de recherche avec titre, URL, snippet et résumé
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
