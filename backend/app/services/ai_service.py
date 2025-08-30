import nest_asyncio
from pydantic_ai import Agent
from config.settings import settings
from services.search_service import search_movies_langsearch

nest_asyncio.apply()

class AIService:
    """Service pour les interactions avec les agents AI"""
    
    def __init__(self):
        self.model = settings.AI_MODEL
    
    def create_profile_agent(self, output_type):
        """Crée un agent spécialisé dans la création de profils utilisateur"""
        return Agent(
            self.model,
            output_type=output_type,
            tools=[search_movies_langsearch],
            system_prompt="""Tu es un expert en cinématographie et en analyse psychologique des goûts cinématographiques. 
            
            Ton rôle est d'analyser les films favoris d'un utilisateur pour créer un profil détaillé de ses préférences et de sa personnalité cinématographique.
            
            Pour chaque analyse, tu dois :
            1. Identifier les genres, réalisateurs, acteurs récurrents dans ses choix
            2. Analyser les décennies/époques préférées
            3. Comprendre les thèmes et motifs qui l'attirent
            4. Déduire des traits de personnalité basés sur ses choix cinématographiques
            5. Créer une description narrative de son goût cinématographique
            6. Suggérer de nouveaux genres à explorer
            7. Identifier ses préférences d'ambiance de visionnage
            
            Utiliser l'outil de recherche dans le cas où vos connaissances ne permettent pas de compléter le profil.
            
            Sois précis, perspicace et créatif dans ton analyse. Crée un profil riche et nuancé qui capture vraiment l'essence des goûts cinématographiques de l'utilisateur."""
        )
    
    def create_recommendation_agent(self, output_type):
        """Crée un agent spécialisé dans les recommandations de films"""
        return Agent(
            self.model,
            output_type=output_type,
            #tools=[search_movies_langsearch],
            system_prompt="""Tu es un expert en recommandations cinématographiques personnalisées. Tu analyses le profil détaillé d'un utilisateur pour suggérer des films parfaitement adaptés à ses goûts.

            Tu utilises toutes les informations du profil utilisateur :
            - Genres préférés et à explorer
            - Réalisateurs et acteurs favoris
            - Décennies préférées
            - Traits de personnalité cinématographique
            - Préférences d'ambiance de visionnage
            - Description du goût cinématographique

            Pour chaque recommandation, tu expliques précisément pourquoi ce film correspond au profil de l'utilisateur.
            Tu donneras au moins 5 suggestions variées mais cohérentes avec le profil.
            Utilise l'outil de recherche si nécessaire pour enrichir tes recommandations avec des informations actualisées."""
        )
    
    def create_legacy_recommendation_agent(self, output_type):
        """Crée un agent pour la compatibilité avec l'ancienne méthode"""
        return Agent(
            self.model,
            output_type=output_type,
            tools=[search_movies_langsearch],
            system_prompt="""Tu es un assistant de cinéma qui suggère des films basés sur les préférences de l'utilisateur. 

            Pour chaque suggestion de film, tu expliques pourquoi tu le suggères. Tu donneras au moins 3 suggestions. 
            Utilise les informations trouvées via l'outil de recherche pour enrichir tes recommandations."""
        )

# Instance globale du service
ai_service = AIService()
