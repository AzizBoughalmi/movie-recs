# Movie Recommendations - Production Deployment Guide

This guide covers all the changes made to make your movie recommendation website production-ready and provides step-by-step deployment instructions.

## 🔧 Changes Made for Production Readiness

### 1. Security Improvements
- **Removed hardcoded secret key** from `backend/app/main.py`
- **Implemented environment-based configuration** in `backend/app/config/settings.py`
- **Removed API key logging** to prevent sensitive data exposure
- **Added proper CORS configuration** using environment variables

### 2. Environment Configuration
- **Created `.env` files** for both backend and frontend
- **Added `.env.production` templates** for production deployment
- **Implemented dynamic API URL configuration** in frontend

### 3. Production Server Setup
- **Installed Gunicorn** as production WSGI server
- **Created startup scripts** for easy production deployment
- **Cleaned up dependencies** in `requirements.txt`

### 4. Code Structure Improvements
- **Centralized configuration management** with validation
- **Removed hardcoded URLs** throughout the application
- **Added proper error handling** for missing environment variables

## 📁 File Changes Summary

### Backend Changes
```
backend/
├── .env                     # Development environment variables
├── .env.production         # Production environment template
├── requirements.txt        # Clean production dependencies
├── start_production.py     # Python production startup script
├── start_production.bat    # Windows batch startup script
└── app/
    ├── main.py            # Updated CORS and session config
    └── config/
        └── settings.py    # Environment-based configuration
```

### Frontend Changes
```
frontend/
├── .env                   # Development environment variables
├── .env.production       # Production environment template
└── src/
    ├── config.js         # API configuration utility
    └── App.jsx          # Updated to use dynamic API URLs
```

## 🚀 Deployment Instructions

### Step 1: Environment Setup

1. **Backend Environment Variables**
   ```bash
   cd backend
   cp .env.production .env
   ```
   
   Edit `.env` with your production values:
   ```env
   SECRET_KEY=your-super-secure-secret-key-here
   API_BASE_URL=https://your-api-domain.com
   FRONTEND_URL=https://your-frontend-domain.com
   TMDB_API_KEY=your-tmdb-api-key
   GOOGLE_API_KEY=your-google-api-key
   ```

2. **Frontend Environment Variables**
   ```bash
   cd frontend
   cp .env.production .env
   ```
   
   Edit `.env` with your production values:
   ```env
   VITE_API_BASE_URL=https://your-api-domain.com
   ```

### Step 2: Install Dependencies

1. **Backend Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Frontend Dependencies**
   ```bash
   cd frontend
   npm install
   ```

### Step 3: Build Frontend for Production

```bash
cd frontend
npm run build
```

This creates a `dist/` folder with optimized production files.

### Step 4: Start Production Server

**Option A: Using Python Script**
```bash
cd backend
python start_production.py
```

**Option B: Using Batch File (Windows)**
```bash
cd backend
start_production.bat
```

**Option C: Manual Gunicorn Command**
```bash
cd backend
python -m gunicorn app.main:app --bind 0.0.0.0:8000 --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

## 🔍 Production Server Configuration Explained

### Gunicorn Settings
- **Workers: 4** - Multiple processes for handling concurrent requests
- **Worker Class: UvicornWorker** - Async support for FastAPI
- **Bind: 0.0.0.0:8000** - Listen on all interfaces, port 8000
- **Timeout: 120s** - Request timeout
- **Max Requests: 1000** - Restart workers after 1000 requests (prevents memory leaks)
- **Preload App: True** - Load application before forking workers (better performance)

### Why These Settings Matter
- **Multiple workers** handle concurrent users effectively
- **UvicornWorker** maintains FastAPI's async capabilities
- **Worker recycling** prevents memory leaks in long-running processes
- **Proper timeouts** prevent hanging requests

## 🌐 Deployment Options

### Option 1: Traditional VPS/Server
1. Upload your code to the server
2. Set up environment variables
3. Install dependencies
4. Run the production startup script
5. Configure reverse proxy (Nginx) if needed

### Option 2: Docker Deployment
Create `Dockerfile` in backend:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "start_production.py"]
```

### Option 3: Cloud Platforms
- **Heroku**: Use `Procfile` with gunicorn command
- **Railway**: Direct deployment with environment variables
- **DigitalOcean App Platform**: Configure build and run commands
- **AWS/GCP/Azure**: Use container services or app services

## 🔒 Security Checklist

- [x] Secret key is environment-based, not hardcoded
- [x] API keys are not logged or exposed
- [x] CORS is properly configured for your domain
- [x] Environment variables are used for all sensitive data
- [ ] HTTPS is enabled (configure on your hosting platform)
- [ ] Database connections are secured (if using external DB)
- [ ] Rate limiting is implemented (consider adding)
- [ ] Input validation is thorough (review your endpoints)

## 📊 Monitoring and Maintenance

### Recommended Additions
1. **Logging**: Implement structured logging
2. **Health Checks**: Add `/health` endpoint
3. **Metrics**: Monitor response times and error rates
4. **Database**: Consider persistent storage for user profiles
5. **Caching**: Implement Redis for API response caching
6. **CDN**: Use CDN for frontend static files

### Log Monitoring
Gunicorn logs to stdout/stderr. In production, redirect these to files:
```bash
python -m gunicorn app.main:app --bind 0.0.0.0:8000 --workers 4 --worker-class uvicorn.workers.UvicornWorker --access-logfile access.log --error-logfile error.log
```

## 🚨 Troubleshooting

### Common Issues
1. **Port already in use**: Change port in startup script
2. **Environment variables not loaded**: Check .env file location and syntax
3. **CORS errors**: Verify FRONTEND_URL matches your domain exactly
4. **Import errors**: Ensure all dependencies are installed

### Testing Production Setup Locally
1. Use `.env.production` with localhost URLs
2. Start the production server
3. Build and serve frontend from `dist/` folder
4. Test all functionality before deploying

## 📝 Next Steps

Your application is now production-ready with the basic setup. Consider these enhancements:

1. **Database Integration**: Add PostgreSQL/MySQL for persistent data
2. **User Authentication**: Implement proper user management
3. **API Rate Limiting**: Prevent abuse
4. **Caching Layer**: Improve performance
5. **Monitoring**: Add application monitoring
6. **Backup Strategy**: Implement data backup procedures

## 🎯 Summary

Your movie recommendation website has been transformed from a development setup to a production-ready application with:

- ✅ Secure environment-based configuration
- ✅ Production-grade server setup (Gunicorn)
- ✅ Clean dependency management
- ✅ Proper CORS and security settings
- ✅ Easy deployment scripts
- ✅ Comprehensive documentation

The application is now ready for deployment to any hosting platform!
