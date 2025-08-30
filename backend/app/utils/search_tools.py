"""
Module refactorisé pour les outils de recherche
Utilise la nouvelle architecture modulaire
"""

from services.search_service import search_movies_langsearch

# Export de la fonction pour compatibilité
__all__ = ['search_movies_langsearch']

# La fonction search_movies_langsearch est maintenant importée du service
# et est disponible pour les agents AI
