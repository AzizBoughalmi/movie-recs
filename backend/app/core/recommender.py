from models.profile import Profile
from models.movie import AgentMovies, Movies, Movie
from services.ai_service import ai_service
from services.tmdb_service import tmdb_service

class MovieRecommender:
    """Classe responsable de la génération de recommandations de films"""
    
    def __init__(self):
        self.ai_service = ai_service
        self.tmdb_service = tmdb_service
    
    def _convert_agent_movies_to_movies(self, agent_movies: AgentMovies) -> Movies:
        """
        Convertit les films de l'agent en films enrichis avec les posters TMDB
        
        Args:
            agent_movies: Résultats de l'agent sans posters
        
        Returns:
            Movies: Films enrichis avec les posters TMDB
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
        Génère des recommandations de films basées sur un profil utilisateur
        
        Args:
            user_profile: Profil cinématographique de l'utilisateur
            query: Requête optionnelle pour personnaliser la recherche
        
        Returns:
            Movies: Films recommandés avec posters
        """
        # Utiliser le service AI pour créer l'agent
        agent = self.ai_service.create_recommendation_agent(AgentMovies)
        
        # Construire la requête basée sur le profil
        profile_summary = f"""
Profil :
- Films déjà vus : {', '.join(user_profile.movies_watched) if user_profile.favorite_genres else 'Non spécifiés'}
- Genres favoris : {', '.join(user_profile.favorite_genres) if user_profile.favorite_genres else 'Non spécifiés'}
- Réalisateurs favoris : {', '.join(user_profile.favorite_directors) if user_profile.favorite_directors else 'Non spécifiés'}
- Acteurs favoris : {', '.join(user_profile.favorite_actors) if user_profile.favorite_actors else 'Non spécifiés'}
- Décennies préférées : {', '.join(user_profile.preferred_decades) if user_profile.preferred_decades else 'Non spécifiées'}
- Préférences cinématographiques : {user_profile.movie_preferences}
- Traits de personnalité : {user_profile.personality_traits}
- Description du goût : {user_profile.cinematic_taste_description}
- Genres à explorer : {', '.join(user_profile.recommended_genres_to_explore) if user_profile.recommended_genres_to_explore else 'Non spécifiés'}
- Préférences d'ambiance : {', '.join(user_profile.viewing_mood_preferences) if user_profile.viewing_mood_preferences else 'Non spécifiées'}
"""
        
        if query:
            user_query = f"{profile_summary}\n\nRequête spécifique : {query}\n\nBasé sur ce profil détaillé, recommande des films parfaitement adaptés."
        else:
            user_query = f"{profile_summary}\n\nBasé sur ce profil cinématographique détaillé, recommande des films qui correspondent parfaitement aux goûts et à la personnalité de cet utilisateur."
        
        # Lancer l'agent et récupérer les résultats
        result = agent.run_sync(user_query)
        
        # Convertir et enrichir avec les posters TMDB
        return self._convert_agent_movies_to_movies(result.output)
    
    def get_recommendations_legacy(self, liked_movies: list[str], query: str | None = None) -> Movies:
        """
        Méthode de compatibilité pour l'ancienne approche basée sur une liste de films
        
        Args:
            liked_movies: Liste des films aimés par l'utilisateur
            query: Requête optionnelle
        
        Returns:
            Movies: Films recommandés avec posters
        """
        # Utiliser le service AI pour créer l'agent legacy
        agent = self.ai_service.create_legacy_recommendation_agent(AgentMovies)
        
        # Construire la requête
        if query:
            user_query = f"Voici les films que j'aime : {', '.join(liked_movies)}. {query}"
        else:
            user_query = f"Voici les films que j'aime : {', '.join(liked_movies)}. Peux-tu me suggérer des films similaires ?"
        
        # Lancer l'agent et récupérer les résultats
        result = agent.run_sync(user_query)
        
        # Convertir et enrichir avec les posters TMDB
        return self._convert_agent_movies_to_movies(result.output)

# Instance globale du recommandeur
movie_recommender = MovieRecommender()

# Fonctions pour compatibilité avec l'ancien code
def get_movie_recommendations_from_profile(user_profile: Profile, query: str | None = None) -> Movies:
    """Fonction de compatibilité pour l'ancien code"""
    return movie_recommender.get_recommendations_from_profile(user_profile, query)

def get_movie_recommendations(liked_movies: list[str], query: str | None = None) -> Movies:
    """Fonction de compatibilité pour l'ancien code (DEPRECATED)"""
    return movie_recommender.get_recommendations_legacy(liked_movies, query)
