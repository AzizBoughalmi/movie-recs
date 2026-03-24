# 🎬 Heroku Docker Deployment Checklist

## ✅ Implementation Complete

All files have been created and modified for Heroku Docker deployment.

### Files Created
- ✅ `Dockerfile` — Multi-stage build (frontend + backend)
- ✅ `.dockerignore` — Exclude unnecessary files from Docker context
- ✅ `.env.example` (root) — Environment variables template with Heroku notes

### Files Modified
- ✅ `backend/app/main.py` — Added static file mounting + SPA fallback
- ✅ `backend/start_production.py` — Dynamic `$PORT` from environment
- ✅ `backend/app/config/settings.py` — Made FRONTEND_URL optional
- ✅ `DEPLOYMENT_GUIDE.md` — Added complete Heroku section

---

## 🚀 Deploy to Heroku (6 Steps)

### Prerequisites
```bash
# Install required tools
# - Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli
# - Docker: https://www.docker.com/
# - Git: Already in your project
```

### Step 1: Login to Heroku
```bash
heroku login
# Opens browser to authenticate
```

### Step 2: Create App
```bash
heroku create your-app-name
heroku stack:set container
# Sets app up with container stack
```

### Step 3: Configure Secrets
```bash
heroku config:set \
  TMDB_API_KEY=your_tmdb_api_key \
  GEMINI_API_KEY=your_gemini_api_key \
  LANGSEARCH_API_KEY=your_langsearch_api_key \
  SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# DO NOT set API_BASE_URL, FRONTEND_URL, or VITE_API_BASE_URL
# These are unset on purpose for same-origin deployment
```

**How to get API keys:**
- TMDB_API_KEY: https://www.themoviedb.org/settings/api
- GEMINI_API_KEY: https://makersuite.google.com/app/apikey
- LANGSEARCH_API_KEY: Check your provider
- SECRET_KEY: Generate random secure string (command above does this)

### Step 4: Authenticate Docker Registry
```bash
heroku container:login
# Logs you into Heroku's Docker registry
```

### Step 5: Build & Push Image
```bash
heroku container:push web
# Builds Docker image locally
# Pushes to Heroku's registry
# ~2-3 minutes
```

### Step 6: Release & Open
```bash
heroku container:release web
# Activates the image on your dyno
heroku open
# Opens app in browser
```

---

## 🧪 Verify Deployment

Open your app and check:

1. **Frontend Loads**
   - Visit `https://your-app.herokuapp.com/`
   - Should see React UI (no blank page)

2. **Health Check Works**
   ```bash
   curl https://your-app.herokuapp.com/ping
   # Should return: {"message":"pong"}
   ```

3. **Search Works**
   - Try searching for a movie
   - Should get results from TMDB

4. **Logs Look Good**
   ```bash
   heroku logs --tail
   # Should see "Mounting frontend static files"
   # Should see "CORS Origins configured"
   # No ERROR lines
   ```

---

## 📋 Architecture Summary

### Docker Multi-Stage Build
```
Stage 1: Node.js (frontend-builder)
  ↓
  npm install → npm run build → frontend/dist/

Stage 2: Python (app)
  ↓
  pip install → copy backend files
  ↓
  COPY dist/ from Stage 1
  ↓
  Single production image: ~500-800MB
```

### Running on Heroku
```
Docker Container (1 dyno)
├── FastAPI Server (Gunicorn + Uvicorn)
│   ├── API Routes: /ping, /search, /recommendations, /profile/*
│   └── Static Routes: /, /about, /movies, etc. (React)
└── Listens on $PORT (Heroku assigns dynamically)
```

### Environment Configuration
```
Development (local):
  Backend:
    - API_BASE_URL=http://localhost:8000
    - FRONTEND_URL=http://localhost:5173
  Frontend:
    - VITE_API_BASE_URL=http://localhost:8000
  Behavior: Separate servers, API requests to localhost:8000

Production (Heroku):
  Backend:
    - API_BASE_URL=unset (uses fallback http://localhost:8000, never called)
    - FRONTEND_URL=unset (CORS allows all origins)
  Frontend:
    - VITE_API_BASE_URL=unset (defaults to empty string = same-origin)
  Behavior: Single domain, frontend uses relative paths to call API
```

---

## 🔍 Key Changes Explained

### 1. Dockerfile (Multi-Stage)
- **Why?** Reduces final image size. Frontend build tools not in production.
- **How?** Node stage → builds React → copies `dist/` to Python stage
- **Result?** One image with both frontend and API

### 2. Static File Mounting
Added to `main.py`:
```python
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")
```
- **Why?** Makes frontend files available at web root
- **html=True?** Serves `index.html` for unknown routes (SPA fallback)
- **Result?** React Router handles all URLs on client-side

### 3. Dynamic Port Binding
Added to `start_production.py`:
```python
port = os.getenv("PORT", "8000")
```
- **Why?** Heroku assigns random PORT at runtime
- **Default?** Falls back to 8000 for local testing
- **Result?** Works on any port without code changes

### 4. Flexible CORS
Added to `main.py`:
```python
cors_origins = ["*"] if not settings.FRONTEND_URL else [settings.FRONTEND_URL]
```
- **Why?** Frontend served from same domain (no CORS issues in production)
- **When?** FRONTEND_URL unset on Heroku
- **Result?** No cross-origin errors when deployed

### 5. Frontend Same-Origin Config
Updated `frontend/src/config.js`:
```javascript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';
const getApiUrl = (endpoint) => {
  if (!API_BASE_URL) {
    return `/${endpoint}`;  // Same-origin: relative path
  }
  return `${API_BASE_URL}/${endpoint}`;  // Different origin: absolute URL
}
```
- **Why?** Frontend needs to work on Heroku (same domain) without VITE_API_BASE_URL set
- **How?** When VITE_API_BASE_URL is empty, uses relative paths (`/search`, `/recommendations`)
- **Result?** API calls work from same Heroku domain without config needed

---

## 🚀 Update Deployment (after code changes)
```bash
git add .
git commit -m "Your changes"
heroku container:push web
heroku container:release web
# That's it! App updated in ~1-2 minutes
```

---

## 📊 Dyno Resources
```
Default Heroku dyno: 512 MB RAM
Estimated usage:
  - Python runtime: ~150 MB
  - Dependencies: ~100 MB
  - Frontend assets: ~200 KB (gzipped)
  - Memory for requests: ~100 MB
  
Comfortable? Yes, should work fine.
```

---

## ⚠️ Important Notes

1. **Never commit `.env` files** — Only commit `.env.example`
2. **Secrets go in `heroku config`** — Not in code or files
3. **Frontend built during Docker build** — No manual `npm run build` needed
4. **Both services on one dyno** — Single `web` process type
5. **FRONTEND_URL unset on Heroku** — Handled by CORS logic
6. **No database setup required** — App is stateless (session-based)

---

## 🆘 Troubleshooting

### App crashes on startup?
```bash
heroku logs --tail
# Check for missing API keys or syntax errors
```

### Frontend not loading?
```bash
# Check if dist/ mounted correctly
curl https://your-app.herokuapp.com/assets/
# Should return CSS/JS files
```

### API returns 404?
- Check that routes use `/api/*` pattern
- Verify CORS not blocking requests
- Check `heroku logs` for errors

### Port binding error?
- Verify `start_production.py` uses `PORT` env var
- Check Heroku isn't running old cached image
- Force rebuild: `heroku container:push web --no-cache`

---

## 📈 Next Steps (Optional Enhancements)

1. **Enable HTTPS** — Automatic on Heroku with `*.herokuapp.com` domain
2. **Custom Domain** — Add your own domain (requires paid Heroku account)
3. **Scale** — `heroku ps:scale web=2` for multiple instances
4. **Add Database** — `heroku addons:create heroku-postgresql` for persistence
5. **CI/CD** — Connect GitHub for auto-deploy on push
6. **Monitoring** — `heroku metrics` to track performance

---

## ✨ You're All Set!

Everything is ready for Heroku Docker deployment. Follow the 6 steps above and your app will be live in minutes. 🎉
