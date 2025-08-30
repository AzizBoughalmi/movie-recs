# Movie Recommendations App

Une application de recommandations de films avec un frontend React et un backend Python.

## Structure du projet

```
movie_recs/
├── frontend/          # Application React avec Vite
│   ├── src/
│   ├── public/
│   └── package.json
└── backend/           # API Python
    ├── app/
    │   ├── main.py
    │   └── agent.py
    └── requirements.txt (à créer)
```

## Technologies utilisées

### Frontend
- React 18
- Vite
- Tailwind CSS
- JavaScript/JSX

### Backend
- Python
- FastAPI 
- Agent de recommandation personnalisé

## Installation et démarrage

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Backend
```bash
cd backend
# Créer un environnement virtuel
python -m venv venv
# Activer l'environnement virtuel
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Installer les dépendances (à définir)
pip install -r requirements.txt

# Démarrer le serveur
python app/main.py
```

## Configuration

Les fichiers `.env` sont nécessaires pour la configuration locale mais ne sont pas inclus dans le repository pour des raisons de sécurité.

## Contribution

Ce projet est privé. Pour contribuer, contactez le propriétaire du repository.
