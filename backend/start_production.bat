@echo off
echo Starting Movie Recommendations API in Production Mode...
echo.

REM Check if .env.production exists, otherwise use .env
if exist .env.production (
    echo Using .env.production configuration
    set ENV_FILE=.env.production
) else (
    echo Using .env configuration
    set ENV_FILE=.env
)

echo.
echo Starting server with Gunicorn...
echo Command: python -m gunicorn app.main:app --bind 0.0.0.0:8000 --workers 4 --worker-class uvicorn.workers.UvicornWorker
echo.

python -m gunicorn app.main:app --bind 0.0.0.0:8000 --workers 4 --worker-class uvicorn.workers.UvicornWorker --timeout 120 --keepalive 5 --max-requests 1000 --preload

pause
