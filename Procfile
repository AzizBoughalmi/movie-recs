web: bash -c 'cd /app/backend && gunicorn --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT} --timeout 120 app.main:app'

