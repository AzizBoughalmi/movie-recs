from app.models.profile import Profile
from app.models.movie import AgentMovies, Movies, Movie
from app.services.ai_service import ai_service
from app.services.tmdb_service import tmdb_service

class MovieRecommender:
    """Class responsible for generating movie recommendations"""
    
    def __init__(self):
        self.ai_service = ai_service
        self.tmdb_service = tmdb_service
    
    def _convert_agent_movies_to_movies(self, agent_movies: AgentMovies) -> Movies:
        """
        Converts agent movies to enriched movies with TMDB posters
        
        Args:
            agent_movies: Agent results without posters
        
        Returns:
            Movies: Movies enriched with TMDB posters
        """
        enriched_movies = []
        
        for agent_movie in agent_movies.movies:
            poster_url = self.tmdb_service.search_movie_poster(agent_movie.title, agent_movie.year)
            
            enriched_movie = Movie(
                title=agent_movie.title,
                year=agent_movie.year,
                genre=agent_movie.genre,
                director=agent_movie.director,
                description=agent_movie.description,
                why_recommended=agent_movie.why_recommended,
                rating=agent_movie.rating,
                cast=agent_movie.cast,
                poster_path=poster_url
            )
            enriched_movies.append(enriched_movie)
        
        return Movies(movies=enriched_movies)
    
    def get_recommendations_from_profile(self, user_profile: Profile, query: str | None = None) -> Movies:
        """
        Generates movie recommendations based on a user profile
        
        Args:
            user_profile: User's cinematic profile
            query: Optional query to customize the search
        
        Returns:
            Movies: Recommended movies with posters
        """
        # Use AI service to create the agent
        agent = self.ai_service.create_recommendation_agent(AgentMovies)
        
        # Build the query based on the profile
        profile_summary = f"""
Profile:
- Movies watched: {', '.join(user_profile.movies_watched) if user_profile.favorite_genres else 'Not specified'}
- Favorite genres: {', '.join(user_profile.favorite_genres) if user_profile.favorite_genres else 'Not specified'}
- Favorite directors: {', '.join(user_profile.favorite_directors) if user_profile.favorite_directors else 'Not specified'}
- Favorite actors: {', '.join(user_profile.favorite_actors) if user_profile.favorite_actors else 'Not specified'}
- Preferred decades: {', '.join(user_profile.preferred_decades) if user_profile.preferred_decades else 'Not specified'}
- Movie preferences: {user_profile.movie_preferences}
- Personality traits: {user_profile.personality_traits}
- Taste description: {user_profile.cinematic_taste_description}
- Genres to explore: {', '.join(user_profile.recommended_genres_to_explore) if user_profile.recommended_genres_to_explore else 'Not specified'}
- Mood preferences: {', '.join(user_profile.viewing_mood_preferences) if user_profile.viewing_mood_preferences else 'Not specified'}
"""
        
        if query:
            user_query = f"{profile_summary}\n\nSpecific query: {query}\n\nBased on this detailed profile, recommend perfectly suited movies."
        else:
            user_query = f"{profile_summary}\n\nBased on this detailed cinematic profile, recommend movies that perfectly match this user's tastes and personality."
        
        # Run the agent and retrieve results
        result = agent.run_sync(user_query)
        
        # Convert and enrich with TMDB posters
        return self._convert_agent_movies_to_movies(result.output)
    
    def get_recommendations_legacy(self, liked_movies: list[str], query: str | None = None) -> Movies:
        """
        Compatibility method for the old approach based on a movie list
        
        Args:
            liked_movies: List of movies liked by the user
            query: Optional query
        
        Returns:
            Movies: Recommended movies with posters
        """
        # Use AI service to create the legacy agent
        agent = self.ai_service.create_legacy_recommendation_agent(AgentMovies)
        
        # Build the query
        if query:
            user_query = f"Here are the movies I like: {', '.join(liked_movies)}. {query}"
        else:
            user_query = f"Here are the movies I like: {', '.join(liked_movies)}. Can you suggest similar movies?"
        
        # Run the agent and retrieve results
        result = agent.run_sync(user_query)
        
        # Convert and enrich with TMDB posters
        return self._convert_agent_movies_to_movies(result.output)

# Global instance of the recommender
movie_recommender = MovieRecommender()

# Functions for compatibility with old code
def get_movie_recommendations_from_profile(user_profile: Profile, query: str | None = None) -> Movies:
    """Compatibility function for old code"""
    return movie_recommender.get_recommendations_from_profile(user_profile, query)

def get_movie_recommendations(liked_movies: list[str], query: str | None = None) -> Movies:
    """Compatibility function for old code (DEPRECATED)"""
    return movie_recommender.get_recommendations_legacy(liked_movies, query)
