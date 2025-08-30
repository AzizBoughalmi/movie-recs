import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Configuration centralisée de l'application"""
    
    # API Keys
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    TMDB_API_KEY = os.getenv('TMDB_API_KEY')
    LANGSEARCH_API_KEY = os.getenv('LANGSEARCH_API_KEY')
    
    # API Endpoints
    TMDB_BASE_URL = "https://api.themoviedb.org/3"
    TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
    LANGSEARCH_ENDPOINT = "https://api.langsearch.com/v1/web-search"
    
    # AI Model Configuration
    AI_MODEL = 'gemini-2.0-flash'
    
    # Default values
    DEFAULT_SEARCH_COUNT = 5
    DEFAULT_SEARCH_FRESHNESS = "noLimit"
    API_TIMEOUT = 10

# Instance globale des settings
settings = Settings()
