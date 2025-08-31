import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Configuration centralisée de l'application"""
    
    def __init__(self):
        # API Keys
        self.GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
        self.TMDB_API_KEY = os.getenv('TMDB_API_KEY')
        self.LANGSEARCH_API_KEY = os.getenv('LANGSEARCH_API_KEY')
        
        # Security
        self.SECRET_KEY = os.getenv('SECRET_KEY')
        
        # API Configuration
        self.API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
        self.FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')
        
        # Validate required environment variables
        self._validate_required_vars()
    
    def _validate_required_vars(self):
        """Validate required environment variables"""
        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY environment variable is required")
        if not self.TMDB_API_KEY:
            raise ValueError("TMDB_API_KEY environment variable is required")
        if not self.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is required")
    
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
