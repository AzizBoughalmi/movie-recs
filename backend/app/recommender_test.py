"""
Test pour les recommandations de films
Utilise la nouvelle architecture modulaire avec ProfileCreator et MovieRecommender
"""

from core.profile_creator import ProfileCreator
from core.recommender import MovieRecommender
from models.movie import Movies, Movie
from models.profile import Profile

# Exemple d'utilisation avec les classes
if __name__ == "__main__":
    print("🎬 DÉMONSTRATION DE L'INTÉGRATION PROFILE_CREATOR + MOVIE_RECOMMENDER")
    print("=" * 70)
    
    # Créer les instances des classes
    profile_creator = ProfileCreator()
    movie_recommender = MovieRecommender()
    
    # Étape 1: Créer un profil utilisateur à partir de films favoris
    print("\n📝 ÉTAPE 1: Création du profil utilisateur")
    favorite_movies = ["Home Alone", "The mask"]
    user_name = "Alice"
    
    print(f"Films favoris de {user_name}: {', '.join(favorite_movies)}")
    print("🔄 Création du profil en cours...")
    
    try:
        # Utiliser la méthode de la classe ProfileCreator
        user_profile = profile_creator.create_user_profile(favorite_movies, user_name)
        print("✅ Profil créé avec succès!")
        
        # Afficher un résumé du profil
        print(f"\n👤 PROFIL DE {user_profile.user_name.upper()}:")
        print(f"🎭 Genres favoris: {', '.join(user_profile.favorite_genres[:3])}{'...' if len(user_profile.favorite_genres) > 3 else ''}")
        print(f"🎬 Réalisateurs favoris: {', '.join(user_profile.favorite_directors[:2])}{'...' if len(user_profile.favorite_directors) > 2 else ''}")
        print(f"💭 Traits: {user_profile.personality_traits[:100]}...")
        
        # Étape 2: Générer des recommandations basées sur le profil
        print(f"\n🎯 ÉTAPE 2: Génération de recommandations personnalisées")
        print("🔄 Analyse du profil et recherche de films adaptés...")
        
        # Utiliser la méthode de la classe MovieRecommender
        recommendations = movie_recommender.get_recommendations_from_profile(user_profile)
        
        print(f"✅ {len(recommendations.movies)} recommandations générées!")
        
        # Afficher les résultats
        print(f"\n🎬 FILMS RECOMMANDÉS POUR {user_profile.user_name.upper()}:")
        print("=" * 50)
        
        for i, movie in enumerate(recommendations.movies, 1):
            print(f"\n{i}. 🎭 {movie.title} ({movie.year})")
            print(f"   📂 Genre: {movie.genre}")
            if movie.director:
                print(f"   🎬 Réalisateur: {movie.director}")
            print(f"   💡 Pourquoi recommandé: {movie.why_recommended}")
            if movie.cast:
                print(f"   ⭐ Cast: {', '.join(movie.cast[:3])}{'...' if len(movie.cast) > 3 else ''}")
            if movie.poster_path:
                print(f"   🖼️ Poster: ✅")
            print("   " + "-" * 40)
        
        print(f"\n🎉 DÉMONSTRATION TERMINÉE AVEC SUCCÈS!")
        print("✅ Le système ProfileCreator + MovieRecommender fonctionne parfaitement!")
        
    except Exception as e:
        print(f"❌ Erreur lors de la démonstration: {str(e)}")
        print("\n🔄 Utilisation de l'ancienne méthode comme fallback...")
        
        # Fallback vers l'ancienne méthode avec la classe
        recommendations = movie_recommender.get_recommendations_legacy(favorite_movies)
        
        print("Films recommandés (méthode classique):")
        for movie in recommendations.movies:
            print(f"\n- {movie.title} ({movie.year})")
        print("Films recommandés (méthode classique):")
        for movie in recommendations.movies:
            print(f"\n- {movie.title} ({movie.year})")
            print(f"  Genre: {movie.genre}")
            print(f"  Réalisateur: {movie.director}")
            print(f"  Pourquoi recommandé: {movie.why_recommended}")
