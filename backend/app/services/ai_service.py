
from pydantic_ai import Agent
from app.config.settings import settings
from app.services.search_service import search_movies_langsearch


class AIService:
    """Service for AI agent interactions"""
    
    def __init__(self):
        self.model = settings.AI_MODEL
    
    def create_profile_agent(self, output_type):
        """Creates an agent specialized in user profile creation"""
        return Agent(
            self.model,
            output_type=output_type,
            tools=[search_movies_langsearch],
            system_prompt="""You are an expert in cinematography and psychological analysis of cinematic tastes. 
            
            Your role is to analyze a user's favorite movies to create a detailed profile of their preferences and cinematic personality.
            
            For each analysis, you must:
            1. Identify recurring genres, directors, actors in their choices
            2. Analyze preferred decades/eras
            3. Understand the themes and motifs that attract them
            4. Deduce personality traits based on their cinematic choices
            5. Create a narrative description of their cinematic taste
            6. Suggest new genres to explore
            7. Identify their viewing mood preferences
            
            Use the search tool when your knowledge is not sufficient to complete the profile.
            
            Be precise, insightful and creative in your analysis. Create a rich and nuanced profile that truly captures the essence of the user's cinematic tastes."""
        )
    
    def create_recommendation_agent(self, output_type):
        """Creates an agent specialized in movie recommendations"""
        return Agent(
            self.model,
            output_type=output_type,
            #tools=[search_movies_langsearch],
            system_prompt="""You are an expert in personalized movie recommendations. You analyze a user's detailed profile to suggest movies perfectly suited to their tastes.

            You use all the information from the user profile:
            - Favorite and genres to explore
            - Favorite directors and actors
            - Preferred decades
            - Cinematic personality traits
            - Viewing mood preferences
            - Cinematic taste description

            For each recommendation, you explain precisely why this movie matches the user's profile.
            You will provide at least 5 varied but coherent suggestions with the profile.
            Use the search tool if necessary to enrich your recommendations with updated information."""
        )
    
    def create_legacy_recommendation_agent(self, output_type):
        """Creates an agent for compatibility with the old method"""
        return Agent(
            self.model,
            output_type=output_type,
            tools=[search_movies_langsearch],
            system_prompt="""You are a movie assistant that suggests films based on user preferences. 

            For each movie suggestion, you explain why you suggest it. You will provide at least 3 suggestions. 
            Use the information found via the search tool to enrich your recommendations."""
        )

# Instance globale du service
ai_service = AIService()
