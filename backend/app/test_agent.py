#!/usr/bin/env python3
"""
Script de test pour l'agent de recommandation de films
Tests avec différents cas d'usage et affichage des résultats
"""

import os
import sys
import time
from typing import List
sys.path.append(os.path.dirname(__file__))

from agent import get_movie_recommendations, Movies

def print_separator(title: str, char: str = "=", width: int = 80):
    """Affiche un séparateur avec titre"""
    print(f"\n{char * width}")
    print(f"{title:^{width}}")
    print(f"{char * width}")

def print_movie_results(movies: Movies, test_name: str):
    """Affiche les résultats de recommandation de films de manière claire"""
    print(f"\n🎬 RÉSULTATS POUR: {test_name}")
    print("-" * 60)
    
    if not movies.movies:
        print("❌ Aucune recommandation trouvée")
        return
    
    for i, movie in enumerate(movies.movies, 1):
        print(f"\n📽️  FILM #{i}: {movie.title}")
        print(f"   📅 Année: {movie.year or 'Non spécifiée'}")
        print(f"   🎭 Genre: {movie.genre or 'Non spécifié'}")
        print(f"   🎬 Réalisateur: {movie.director or 'Non spécifié'}")
        print(f"   ⭐ Note: {movie.rating or 'Non spécifiée'}")
        
        if movie.cast:
            cast_str = ", ".join(movie.cast[:3])  # Limiter à 3 acteurs
            if len(movie.cast) > 3:
                cast_str += f" (et {len(movie.cast) - 3} autres)"
            print(f"   👥 Casting: {cast_str}")
        
        print(f"   📖 Description: {movie.description[:150]}{'...' if len(movie.description) > 150 else ''}")
        print(f"   💡 Pourquoi recommandé: {movie.why_recommended[:200]}{'...' if len(movie.why_recommended) > 200 else ''}")
        
        poster_status = "✅ Disponible" if movie.poster_path else "❌ Non trouvé"
        print(f"   🖼️  Poster: {poster_status}")

def test_case_1():
    """Test Case 1: Films d'action/aventure classiques"""
    print_separator("TEST CASE 1: FILMS D'ACTION/AVENTURE CLASSIQUES", "🎯")
    
    liked_movies = ["The Matrix", "Die Hard", "Terminator 2"]
    query = "Je cherche des films d'action avec beaucoup d'effets spéciaux et des héros charismatiques"
    
    print(f"📝 Films aimés: {', '.join(liked_movies)}")
    print(f"💭 Requête personnalisée: {query}")
    
    start_time = time.time()
    try:
        results = get_movie_recommendations(liked_movies, query)
        end_time = time.time()
        
        print(f"⏱️  Temps d'exécution: {end_time - start_time:.2f} secondes")
        print_movie_results(results, "Films d'action/aventure")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        return False

def test_case_2():
    """Test Case 2: Films dramatiques/psychologiques"""
    print_separator("TEST CASE 2: FILMS DRAMATIQUES/PSYCHOLOGIQUES", "🎭")
    
    liked_movies = ["The Shawshank Redemption", "Fight Club", "Inception"]
    query = None  # Test sans requête personnalisée
    
    print(f"📝 Films aimés: {', '.join(liked_movies)}")
    print(f"💭 Requête personnalisée: Aucune (test de base)")
    
    start_time = time.time()
    try:
        results = get_movie_recommendations(liked_movies, query)
        end_time = time.time()
        
        print(f"⏱️  Temps d'exécution: {end_time - start_time:.2f} secondes")
        print_movie_results(results, "Films dramatiques/psychologiques")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        return False

def test_case_3():
    """Test Case 3: Films de science-fiction récents"""
    print_separator("TEST CASE 3: FILMS DE SCIENCE-FICTION RÉCENTS", "🚀")
    
    liked_movies = ["Blade Runner 2049", "Interstellar", "Arrival"]
    query = "Je veux des films de science-fiction récents avec une approche réaliste et philosophique"
    
    print(f"📝 Films aimés: {', '.join(liked_movies)}")
    print(f"💭 Requête personnalisée: {query}")
    
    start_time = time.time()
    try:
        results = get_movie_recommendations(liked_movies, query)
        end_time = time.time()
        
        print(f"⏱️  Temps d'exécution: {end_time - start_time:.2f} secondes")
        print_movie_results(results, "Films de science-fiction récents")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        return False

def run_all_tests():
    """Exécute tous les tests et affiche un résumé"""
    print_separator("🧪 TESTS DE L'AGENT DE RECOMMANDATION DE FILMS", "🎬")
    print("Démarrage des tests automatisés...")
    
    # Variables pour le suivi des résultats
    test_results = []
    total_start_time = time.time()
    
    # Exécution des tests
    tests = [
        ("Test Case 1", test_case_1),
        ("Test Case 2", test_case_2),
        ("Test Case 3", test_case_3)
    ]
    
    for test_name, test_func in tests:
        print(f"\n🔄 Exécution de {test_name}...")
        try:
            result = test_func()
            test_results.append((test_name, result))
            if result:
                print(f"✅ {test_name} terminé avec succès")
            else:
                print(f"❌ {test_name} a échoué")
        except Exception as e:
            print(f"💥 {test_name} a planté: {str(e)}")
            test_results.append((test_name, False))
    
    # Résumé final
    total_end_time = time.time()
    total_time = total_end_time - total_start_time
    
    print_separator("📊 RÉSUMÉ DES TESTS", "📈")
    
    successful_tests = sum(1 for _, result in test_results if result)
    total_tests = len(test_results)
    
    print(f"🎯 Tests exécutés: {total_tests}")
    print(f"✅ Tests réussis: {successful_tests}")
    print(f"❌ Tests échoués: {total_tests - successful_tests}")
    print(f"⏱️  Temps total: {total_time:.2f} secondes")
    print(f"📊 Taux de réussite: {(successful_tests/total_tests)*100:.1f}%")
    
    print("\n📋 Détail des résultats:")
    for test_name, result in test_results:
        status = "✅ RÉUSSI" if result else "❌ ÉCHOUÉ"
        print(f"   {test_name}: {status}")
    
    if successful_tests == total_tests:
        print("\n🎉 TOUS LES TESTS ONT RÉUSSI!")
    else:
        print(f"\n⚠️  {total_tests - successful_tests} test(s) ont échoué")
    
    print_separator("FIN DES TESTS", "🏁")

if __name__ == "__main__":
    # Vérification des variables d'environnement
    required_env_vars = ["GEMINI_API_KEY", "LANGSEARCH_API_KEY", "TMDB_API_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Variables d'environnement manquantes:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Assurez-vous que votre fichier .env contient toutes les clés API nécessaires")
        sys.exit(1)
    
    print("🔑 Toutes les variables d'environnement sont présentes")
    
    # Exécution des tests
    run_all_tests()
