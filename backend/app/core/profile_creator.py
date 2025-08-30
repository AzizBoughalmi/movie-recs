from models.profile import Profile
from services.ai_service import ai_service

class ProfileCreator:
    """Classe responsable de la création de profils utilisateur"""
    
    def __init__(self):
        self.ai_service = ai_service
    
    def create_user_profile(self, favorite_movies: list[str], user_name: str = "Utilisateur") -> Profile:
        """
        Analyse les films favoris de l'utilisateur pour créer un profil cinématographique détaillé
        
        Args:
            favorite_movies: Liste des titres de films favoris de l'utilisateur
            user_name: Nom de l'utilisateur (optionnel)
        
        Returns:
            Profile: Profil cinématographique détaillé de l'utilisateur
        """
        # Utiliser le service AI pour créer l'agent
        profile_agent = self.ai_service.create_profile_agent(Profile)
        
        # Construire la requête d'analyse
        user_query = f"""Analyse les films favoris de {user_name} pour créer son profil cinématographique : {', '.join(favorite_movies)}.
        
        Crée un profil détaillé qui inclut :
        - Les genres préférés
        - Les réalisateurs et acteurs favoris
        - Les décennies/époques préférées
        - Une analyse de ses préférences cinématographiques
        - Des traits de personnalité déduits de ses choix
        - Une description narrative de son goût cinématographique
        - Des genres recommandés à explorer
        - Ses préférences d'ambiance de visionnage
        """
        
        # Lancer l'agent et récupérer le profil
        result = profile_agent.run_sync(user_query)
        return result.output

# Instance globale du créateur de profils
profile_creator = ProfileCreator()

# Fonction pour compatibilité avec l'ancien code
def create_user_profile(favorite_movies: list[str], user_name: str = "Utilisateur") -> Profile:
    """Fonction de compatibilité pour l'ancien code"""
    return profile_creator.create_user_profile(favorite_movies, user_name)
