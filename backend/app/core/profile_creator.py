from app.models.profile import Profile
from app.services.ai_service import ai_service

class ProfileCreator:
    """Class responsible for user profile creation"""
    
    def __init__(self):
        self.ai_service = ai_service
    
    def create_user_profile(self, favorite_movies: list[str], ) -> Profile:
        """
        Analyzes user's favorite movies to create a detailed cinematic profile
        
        Args:
            favorite_movies: List of user's favorite movie titles

        
        Returns:
            Profile: Detailed cinematic profile of the user
        """
        # Use AI service to create the agent
        profile_agent = self.ai_service.create_profile_agent(Profile)
        
        # Build the analysis query
        user_query = f"""Analyze my favorite movies to create my cinematic profile: {', '.join(favorite_movies)}.
        
        Create a detailed profile that includes:
        - Favorite genres
        - Favorite directors and actors
        - Preferred decades/eras
        - Analysis of cinematic preferences
        - Personality traits deduced from choices
        - Narrative description of cinematic taste
        - Recommended genres to explore
        - Viewing mood preferences
        """
        
        # Run the agent and retrieve the profile
        result = profile_agent.run_sync(user_query)
        return result.output

# Global instance of the profile creator
profile_creator = ProfileCreator()

# Function for compatibility with old code
def create_user_profile(favorite_movies: list[str] ) -> Profile:
    """Compatibility function for old code"""
    return profile_creator.create_user_profile(favorite_movies)
