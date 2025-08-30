import React, { useState, useRef } from "react";
import axios from "axios";

function App() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Référence pour le scroll automatique vers les recommandations
  const recommendationsRef = useRef(null);

  const handleSearch = async () => {
    if (!query.trim()) return;

    try {
      const res = await axios.get(`http://localhost:8000/search`, {
        params: { query }
      });
      setResults(res.data);
    } catch (err) {
      console.error("Erreur lors de la recherche :", err);
    }
  };

  const addToFavorites = (movie) => {
    if (!favorites.find((f) => f.id === movie.id)) {
      setFavorites([...favorites, movie]);
    }
  };

  const removeFromFavorites = (movieId) => {
    setFavorites(favorites.filter(f => f.id !== movieId));
  };

  // Fonction utilitaire pour vérifier si un film est dans les favoris
  const isInFavorites = (movie) => {
    return favorites.some(f => f.id === movie.id);
  };

  // Fonction utilitaire pour obtenir les classes CSS conditionnelles
  const getMovieCardClasses = (movie) => {
    const baseClasses = "bg-gray-800 rounded-2xl p-4 shadow-md hover:shadow-lg transition ease-in-out duration-300 transform hover:scale-105";
    const favoriteClasses = "opacity-60 bg-gray-700 border-2 border-teal-500";
    
    return isInFavorites(movie) ? `${baseClasses} ${favoriteClasses}` : baseClasses;
  };

  // Fonction utilitaire pour obtenir le texte et les classes du bouton
  const getButtonProps = (movie) => {
    if (isInFavorites(movie)) {
      return {
        text: "✅ Déjà ajouté",
        classes: "w-full px-4 py-2 bg-gray-600 text-gray-400 font-medium rounded-xl cursor-not-allowed",
        disabled: true
      };
    }
    return {
      text: "➕ Ajouter aux favoris",
      classes: "w-full px-4 py-2 bg-teal-500 hover:bg-teal-400 text-white font-medium rounded-xl transition ease-in-out duration-300",
      disabled: false
    };
  };

  const getRecommendations = async () => {
    if (favorites.length === 0) {
      alert("Ajoutez d'abord des films à vos favoris !");
      return;
    }

    setLoading(true);
    try {
      const favoriteTitles = favorites.map(f => f.title || f.name);
      const res = await axios.post(`http://localhost:8000/recommendations`, {
        favorites: favoriteTitles,
        query: "Suggère-moi des films similaires à mes favoris"
      });
      
      const newRecommendations = res.data.movies || [];
      setRecommendations(newRecommendations);
      
      // Effacer les résultats de recherche précédents et le champ de recherche
      setResults([]);
      setQuery("");
      
      // Scroll automatique vers les recommandations après un petit délai
      if (newRecommendations.length > 0) {
        setTimeout(() => {
          recommendationsRef.current?.scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
          });
        }, 100);
      }
    } catch (err) {
      console.error("Erreur lors de la génération des recommandations :", err);
      alert("Erreur lors de la génération des recommandations");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-gray-300">
      {/* Header */}
      <header className="bg-gray-800 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-4xl font-bold text-white text-center mb-8">
            🎬 <span className="text-teal-400">Movie Recs</span>
          </h1>
          
          {/* Search Section */}
          <div className="flex flex-col sm:flex-row gap-4 max-w-2xl mx-auto">
            <input
              type="text"
              placeholder="Rechercher un film ou une série..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              className="flex-1 px-4 py-3 bg-gray-700 border border-gray-600 rounded-2xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent transition ease-in-out duration-300"
            />
            <button
              onClick={handleSearch}
              className="px-6 py-3 bg-teal-500 hover:bg-teal-400 text-white font-semibold rounded-2xl transition ease-in-out duration-300 shadow-md hover:shadow-lg transform hover:scale-105"
            >
              🔍 Rechercher
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Layout en deux colonnes sur desktop, vertical sur mobile */}
        <div className="flex flex-col lg:flex-row lg:gap-8 mb-12">
          {/* Colonne principale - Résultats de recherche */}
          <div className="flex-1 lg:w-2/3">
            {results.length > 0 && (
              <section className="mb-8 lg:mb-0">
                <h2 className="text-2xl font-semibold text-white mb-6">Résultats de recherche</h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-2 xl:grid-cols-3 gap-6">
                  {results.map((item) => {
                    const buttonProps = getButtonProps(item);
                    return (
                      <div
                        key={item.id}
                        className={getMovieCardClasses(item)}
                      >
                        {item.poster_path && (
                          <img
                            src={item.poster_path}
                            alt={item.title || item.name}
                            className={`w-full h-64 object-cover rounded-xl mb-4 ${isInFavorites(item) ? 'opacity-70' : ''}`}
                          />
                        )}
                        <h4 className={`text-lg font-semibold mb-2 line-clamp-2 ${isInFavorites(item) ? 'text-gray-400' : 'text-white'}`}>
                          {item.title || item.name}
                        </h4>
                        <p className={`mb-4 ${isInFavorites(item) ? 'text-gray-500' : 'text-indigo-400'}`}>
                          {item.media_type === "movie" ? "🎥 Film" : "📺 Série"}
                        </p>
                        <button
                          onClick={() => !buttonProps.disabled && addToFavorites(item)}
                          disabled={buttonProps.disabled}
                          className={buttonProps.classes}
                        >
                          {buttonProps.text}
                        </button>
                      </div>
                    );
                  })}
                </div>
              </section>
            )}
          </div>

          {/* Colonne sidebar - Favoris (ne s'affiche que s'il y a des favoris) */}
          {favorites.length > 0 && (
            <div className="lg:w-1/3 lg:min-w-0">
              <section className="lg:sticky lg:top-8">
                <div className="flex flex-col sm:flex-row lg:flex-col sm:items-center lg:items-start sm:justify-between lg:justify-start mb-6">
                  <h2 className="text-2xl font-semibold text-white mb-4 sm:mb-0 lg:mb-4">
                    Favoris 
                    <span className="ml-2 px-3 py-1 bg-teal-500 text-white text-sm font-medium rounded-full">
                      {favorites.length}
                    </span>
                  </h2>
                  
                  <button
                    onClick={getRecommendations}
                    disabled={loading}
                    className={`w-full sm:w-auto lg:w-full px-6 py-3 font-semibold rounded-2xl transition ease-in-out duration-300 shadow-md hover:shadow-lg ${
                      loading
                        ? "bg-gray-600 text-gray-400 cursor-not-allowed"
                        : "bg-teal-500 hover:bg-teal-400 text-white transform hover:scale-105"
                    }`}
                  >
                    {loading ? "⏳ Génération..." : "🎯 Obtenir des recommandations"}
                  </button>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 gap-4">
                  {favorites.map((fav) => (
                    <div
                      key={fav.id}
                      className="bg-gray-800 border-2 border-teal-500 rounded-2xl p-4 shadow-md hover:shadow-lg transition ease-in-out duration-300 transform hover:scale-105"
                    >
                      <div className="flex lg:flex-col gap-4">
                        {fav.poster_path && (
                          <img
                            src={fav.poster_path}
                            alt={fav.title || fav.name}
                            className="w-20 h-28 lg:w-full lg:h-48 object-cover rounded-xl flex-shrink-0"
                          />
                        )}
                        <div className="flex-1 lg:flex-none">
                          <h4 className="text-base lg:text-lg font-semibold text-white mb-2 line-clamp-2">
                            {fav.title || fav.name}
                          </h4>
                          <p className="text-indigo-400 mb-3 text-sm lg:text-base">
                            {fav.media_type === "movie" ? "🎥 Film" : "📺 Série"}
                          </p>
                          <button
                            onClick={() => removeFromFavorites(fav.id)}
                            className="w-full px-3 py-2 bg-red-500 hover:bg-red-400 text-white font-medium rounded-xl transition ease-in-out duration-300 text-sm lg:text-base"
                          >
                            ❌ Retirer
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            </div>
          )}
        </div>

        {/* Recommendations Section */}
        {recommendations.length > 0 && (
          <section ref={recommendationsRef}>
            <h2 className="text-2xl font-semibold text-white mb-6">
              🎯 <span className="text-teal-400">Recommandations pour vous</span>
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {recommendations.map((movie, index) => (
                <div
                  key={index}
                  className="bg-gradient-to-br from-gray-800 to-gray-700 border-2 border-teal-400 rounded-2xl p-6 shadow-lg hover:shadow-xl transition ease-in-out duration-300 transform hover:scale-105"
                >
                  {movie.poster_path && (
                    <img
                      src={movie.poster_path}
                      alt={movie.title}
                      className="w-full h-80 object-cover rounded-xl mb-4"
                    />
                  )}
                  <h3 className="text-xl font-bold text-white mb-3">{movie.title}</h3>
                  
                  <div className="space-y-2 text-sm">
                    {movie.year && (
                      <p><span className="text-teal-400 font-semibold">Année:</span> <span className="text-gray-300">{movie.year}</span></p>
                    )}
                    {movie.genre && (
                      <p><span className="text-teal-400 font-semibold">Genre:</span> <span className="text-gray-300">{movie.genre}</span></p>
                    )}
                    {movie.director && (
                      <p><span className="text-teal-400 font-semibold">Réalisateur:</span> <span className="text-gray-300">{movie.director}</span></p>
                    )}
                    {movie.rating && (
                      <p><span className="text-teal-400 font-semibold">Note:</span> <span className="text-amber-400">{movie.rating}</span></p>
                    )}
                    {movie.cast && movie.cast.length > 0 && (
                      <p><span className="text-teal-400 font-semibold">Cast:</span> <span className="text-gray-300">{movie.cast.join(", ")}</span></p>
                    )}
                  </div>

                  {movie.description && (
                    <div className="mt-4">
                      <p className="text-teal-400 font-semibold mb-2">Description:</p>
                      <p className="text-gray-300 text-sm leading-relaxed">{movie.description}</p>
                    </div>
                  )}

                  <div className="mt-4 p-4 bg-gray-900 rounded-xl">
                    <p className="text-teal-400 font-semibold mb-2">Pourquoi recommandé:</p>
                    <p className="text-gray-300 text-sm leading-relaxed">{movie.why_recommended}</p>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
