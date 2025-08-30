import time
from threading import Lock
from functools import wraps
from typing import Callable, Any
import logging

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
langsearch_limiter = RateLimiter(min_interval=2.0)
