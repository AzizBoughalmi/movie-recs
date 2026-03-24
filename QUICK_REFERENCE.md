# 🚀 Heroku Deployment Quick Reference

## Files Created ✨
```
✅ Dockerfile              - Multi-stage build
✅ .dockerignore           - Exclude dev files  
✅ .env.example            - Env template
✅ HEROKU_DEPLOYMENT.md    - Step-by-step guide
✅ HEROKU_DEPLOYMENT_COMPLETE.md - Full guide with troubleshooting
✅ IMPLEMENTATION_SUMMARY.md  - What changed & how it works
```

## Code Changes 🔧
```
✅ backend/app/main.py           - Mount frontend, flexible CORS
✅ backend/start_production.py   - Dynamic $PORT from environment
✅ backend/app/config/settings.py - Optional FRONTEND_URL
✅ frontend/src/config.js        - Same-origin by default
✅ frontend/.env.example         - Updated documentation
✅ DEPLOYMENT_GUIDE.md           - Added Heroku section
```

## Deploy in 6 Steps 🎯

```bash
# 1. Login
heroku login

# 2. Create app
heroku create YOUR-APP-NAME
heroku stack:set container

# 3. Set API keys
heroku config:set \
  TMDB_API_KEY=xxx \
  GEMINI_API_KEY=yyy \
  LANGSEARCH_API_KEY=zzz \
  SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# 4. Docker login
heroku container:login

# 5. Build & push (2-3 min)
heroku container:push web

# 6. Release & open
heroku container:release web
heroku open
```

## Verify Deployment ✅

```bash
# Frontend loads
curl https://YOUR-APP-NAME.herokuapp.com/

# API responds
curl https://YOUR-APP-NAME.herokuapp.com/ping

# View logs
heroku logs --tail
```

## Key Concepts 💡

| Concept | Explanation |
|---------|-------------|
| multi-stage | Node builds frontend → Python inherits dist/ → single image |
| $PORT | Heroku sets dynamically; app reads from environment |
| same-origin | Frontend & API on same domain → no CORS issues |
| static mount | FastAPI serves frontend files from `frontend/dist/` |
| SPA fallback | Unknown routes return index.html (React Router handles) |

## Environment Variables 🔐

| Variable | Dev | Heroku | Why |
|----------|-----|--------|-----|
| TMDB_API_KEY | set | set | Required API key |
| GEMINI_API_KEY | set | set | Required API key |
| LANGSEARCH_API_KEY | set | set | Required API key |
| SECRET_KEY | set | set | Session encryption |
| API_BASE_URL | http://localhost:8000 | **unset** | Same origin on Heroku |
| FRONTEND_URL | http://localhost:5173 | **unset** | Same origin on Heroku |
| VITE_API_BASE_URL | http://localhost:8000 | **unset** | Frontend uses relative paths |

## Architecture 🏗️

```
Docker Image (1 dyno)
  Gunicorn + Uvicorn
    FastAPI App
      ├─ GET /ping → API
      ├─ GET /search → API
      ├─ POST /recommendations → API
      ├─ GET / → frontend/dist/index.html
      ├─ GET /assets/* → frontend/dist/assets/*
      └─ GET /* → frontend/dist/index.html (SPA fallback)
```

## Update Workflow 🔄

```bash
# Make code changes
git add .
git commit -m "Your changes"

# Deploy
heroku container:push web
heroku container:release web

# Done! Live in ~1-2 min
```

## Troubleshooting 🆘

| Problem | Solution |
|---------|----------|
| App crashes | `heroku logs --tail` check for API key missing |
| Frontend won't load | Check `/` route returns index.html |
| API calls fail | Verify CORS not blocking (check browser console) |
| Port error | Verify `PORT = os.getenv("PORT", "8000")` in start_production.py |
| Image too large | Check requirements.txt, remove unused packages |

## API Keys 🔑

| Key | Get From |
|-----|----------|
| TMDB_API_KEY | https://www.themoviedb.org/settings/api |
| GEMINI_API_KEY | https://makersuite.google.com/app/apikey |
| LANGSEARCH_API_KEY | Your provider |
| SECRET_KEY | Generate: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |

## Resources 📚

- **Step-by-step**: HEROKU_DEPLOYMENT.md
- **Full guide**: HEROKU_DEPLOYMENT_COMPLETE.md
- **What changed**: IMPLEMENTATION_SUMMARY.md
- **Heroku docs**: https://devcenter.heroku.com/articles/container-registry-and-runtime

---

**Ready?** Start with `heroku login` 🚀
