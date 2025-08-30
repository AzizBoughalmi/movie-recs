# Système de Prompt Dynamique

## Vue d'ensemble

Le système de prompt pour l'agent de recommandation de films a été refactorisé pour utiliser un fichier markdown externe au lieu d'un prompt hardcodé dans le code Python.

## Architecture

### Fichiers impliqués

- **`system_prompt.md`** : Contient le prompt système en format markdown
- **`agent.py`** : Contient la fonction `load_system_prompt()` pour charger le prompt
- **`test_system_prompt.py`** : Script de test pour vérifier le chargement

### Fonction `load_system_prompt()`

```python
def load_system_prompt() -> str:
    """
    Charge le prompt système depuis le fichier markdown
    
    Returns:
        str: Le contenu du prompt système
    """
```

#### Fonctionnalités

- **Chargement dynamique** : Lit le contenu du fichier `system_prompt.md`
- **Gestion d'erreurs** : En cas d'échec, utilise un prompt de fallback
- **Logging** : Enregistre les succès et échecs de chargement
- **Encodage UTF-8** : Support complet des caractères français

## Avantages

### 1. **Maintenabilité**
- Modification du prompt sans toucher au code Python
- Séparation claire entre logique et contenu
- Versioning indépendant du prompt

### 2. **Flexibilité**
- Format markdown pour une meilleure lisibilité
- Structure hiérarchique avec titres et sections
- Facilité d'édition avec n'importe quel éditeur

### 3. **Robustesse**
- Système de fallback en cas d'erreur
- Logging détaillé pour le debugging
- Gestion des exceptions

## Utilisation

### Modifier le prompt système

1. Éditer le fichier `system_prompt.md`
2. Sauvegarder les modifications
3. Redémarrer l'application (le prompt est rechargé à chaque appel)

### Tester le chargement

```bash
cd backend/app
python test_system_prompt.py
```

### Structure du prompt markdown

```markdown
# Assistant de Cinéma - Prompt Système

Tu es un assistant de cinéma expert...

## Objectifs principaux
- Point 1
- Point 2

## Instructions détaillées
### Sous-section
Contenu détaillé...
```

## Intégration dans l'agent

Le prompt est chargé automatiquement dans la fonction `get_movie_recommendations()` :

```python
# Charger le prompt système depuis le fichier markdown
system_prompt = load_system_prompt()

# Créer l'agent avec le prompt personnalisé
agent = Agent(
    'gemini-2.0-flash',
    output_type=AgentMovies,
    tools=[search_movies_langsearch],
    system_prompt=system_prompt
)
```

## Logging

Le système génère des logs détaillés :

```
INFO - ✅ System prompt loaded from /path/to/system_prompt.md
ERROR - ❌ Error loading system prompt: [error details]
WARNING - ⚠️ Using fallback hardcoded prompt
```

## Fallback

En cas d'erreur de chargement, un prompt minimal est utilisé :

```python
fallback_prompt = """Tu es un assistant de cinéma qui suggère des films basés sur les préférences de l'utilisateur. 

Pour chaque suggestion de film, tu expliques pourquoi tu le suggères. Tu donneras au moins 3 suggestions. 
Utilise les informations trouvées via l'outil de recherche pour enrichir tes recommandations."""
```

## Bonnes pratiques

### Édition du prompt
- Utiliser un éditeur markdown pour la prévisualisation
- Tester après chaque modification importante
- Maintenir la structure hiérarchique

### Déploiement
- Vérifier que le fichier `system_prompt.md` est inclus dans le déploiement
- Tester le chargement en environnement de production
- Surveiller les logs pour détecter les erreurs

### Versioning
- Commiter les modifications du prompt avec des messages descriptifs
- Considérer l'impact sur les réponses de l'agent
- Documenter les changements majeurs
