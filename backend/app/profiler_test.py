"""
Test pour la création de profils utilisateur
Utilise la nouvelle architecture modulaire avec ProfileCreator
"""

import nest_asyncio
from core.profile_creator import ProfileCreator
from models.profile import Profile

# Appliquer nest_asyncio pour permettre les boucles d'événements imbriquées
nest_asyncio.apply()

# Exemple d'utilisation avec la classe ProfileCreator
if __name__ == "__main__":
    # Créer une instance du ProfileCreator
    profile_creator = ProfileCreator()
    
    # Films favoris de l'utilisateur
    favorite_movies = ["Fight club" , "shutter island"]
    user_name = "John"
    
    # Créer le profil utilisateur en utilisant la méthode de la classe
    user_profile = profile_creator.create_user_profile(favorite_movies, user_name)
    
    # Afficher le profil
    print(f"\n🎭 PROFIL CINÉMATOGRAPHIQUE DE {user_profile.user_name.upper()}")
    print("=" * 50)
    
    print(f"\n🎬 Genres favoris: {', '.join(user_profile.favorite_genres)}")
    print(f"🎥 Réalisateurs favoris: {', '.join(user_profile.favorite_directors)}")
    print(f"⭐ Acteurs favoris: {', '.join(user_profile.favorite_actors)}")
    print(f"📅 Décennies préférées: {', '.join(user_profile.preferred_decades)}")
    
    print(f"\n💭 Préférences cinématographiques:")
    print(user_profile.movie_preferences)
    
    print(f"\n🧠 Traits de personnalité:")
    print(user_profile.personality_traits)
    
    print(f"\n🎨 Description du goût cinématographique:")
    print(user_profile.cinematic_taste_description)
    
    print(f"\n🔍 Genres recommandés à explorer: {', '.join(user_profile.recommended_genres_to_explore)}")
    print(f"🌙 Préférences d'ambiance: {', '.join(user_profile.viewing_mood_preferences)}")
