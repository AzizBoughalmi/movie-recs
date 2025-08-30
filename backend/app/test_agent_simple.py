#!/usr/bin/env python3
"""
Script de test simple pour l'agent de recommandation de films
Version allégée pour des tests rapides
"""

import os
import sys
import time
sys.path.append(os.path.dirname(__file__))

from agent import get_movie_recommendations

def test_simple():
    """Test simple avec un seul cas"""
    print("🎬 TEST SIMPLE DE L'AGENT")
    print("=" * 50)
    
    # Test avec des films populaires
    liked_movies = ["spiderman", "houdini"]
    
    print(f"📝 Films aimés: {', '.join(liked_movies)}")
    print("🔄 Génération des recommandations...")
    
    start_time = time.time()
    try:
        results = get_movie_recommendations(liked_movies)
        end_time = time.time()
        
        print(f"⏱️  Temps: {end_time - start_time:.2f}s")
        print(f"🎯 Nombre de recommandations: {len(results.movies)}")
        
        print("\n🎬 RECOMMANDATIONS:")
        print("-" * 30)
        
        for i, movie in enumerate(results.movies, 1):
            print(f"\n{i}. {movie.title} ({movie.year})")
            print(f"   Genre: {movie.genre}")
            print(f"   Réalisateur: {movie.director}")
            print(f"   Pourquoi: {movie.why_recommended}...")
            poster = "✅" if movie.poster_path else "❌"
            print(f"   Poster: {poster}")
        
        print("\n✅ Test terminé avec succès!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

if __name__ == "__main__":
    # Vérification rapide des variables d'environnement
    if not all(os.getenv(var) for var in ["GEMINI_API_KEY", "LANGSEARCH_API_KEY", "TMDB_API_KEY"]):
        print("❌ Variables d'environnement manquantes")
        print("💡 Vérifiez votre fichier .env")
        sys.exit(1)
    
    test_simple()
