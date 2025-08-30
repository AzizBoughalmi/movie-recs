import time
import requests
import random
from functools import wraps
from typing import Callable, Any
import logging

logger = logging.getLogger(__name__)

def retry_on_429(max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0, jitter: bool = True):
    """
    Décorateur pour retry automatique sur erreur 429 avec backoff exponentiel et jitter
    
    Args:
        max_retries: Nombre maximum de tentatives
        base_delay: Délai de base en secondes (défaut: 1.0)
        max_delay: Délai maximum en secondes (défaut: 60.0)
        jitter: Ajouter une composante aléatoire pour éviter l'effet thundering herd
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    logger.debug(f"Tentative {attempt + 1}/{max_retries + 1} pour {func.__name__}")
                    return func(*args, **kwargs)
                    
                except requests.exceptions.HTTPError as e:
                    last_exception = e
                    
                    if e.response.status_code == 429:
                        if attempt < max_retries:
                            # Calcul du délai avec backoff exponentiel
                            exponential_delay = base_delay * (2 ** attempt)
                            
                            # Ajouter du jitter (composante aléatoire)
                            if jitter:
                                jitter_component = random.uniform(0, 1)
                                delay = exponential_delay + jitter_component
                            else:
                                delay = exponential_delay
                            
                            # Limiter le délai maximum
                            delay = min(delay, max_delay)
                            
                            logger.warning(f"Erreur 429 détectée, attente de {delay:.2f}s avant retry...")
                            print(f"⚠️ Rate limit atteint, attente de {delay:.2f}s... (tentative {attempt + 1}/{max_retries + 1})")
                            time.sleep(delay)
                            continue
                        else:
                            logger.error(f"Échec après {max_retries + 1} tentatives")
                            print(f"❌ Échec définitif après {max_retries + 1} tentatives")
                    
                    # Re-raise pour les autres erreurs HTTP
                    raise e
                    
                except Exception as e:
                    # Re-raise immédiatement pour les autres types d'erreurs
                    raise e
            
            # Si on arrive ici, toutes les tentatives ont échoué
            if last_exception:
                raise last_exception
            else:
                raise RuntimeError("Toutes les tentatives ont échoué sans exception capturée")
            
        return wrapper
    return decorator
