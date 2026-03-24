#!/usr/bin/env python3
"""
Production startup script for the Movie Recommendations API
This script configures and starts the FastAPI application using Gunicorn for production deployment.
"""

import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

def main():
    """Start the FastAPI application with Gunicorn in production mode."""
    
    # Ensure we're in the backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # Load environment variables from .env.production if it exists, otherwise .env
    env_file = ".env.production" if Path(".env.production").exists() else ".env"
    if Path(env_file).exists():
        load_dotenv(env_file)
        print(f"✅ Loaded environment from: {env_file}")
    else:
        print(f"⚠️  No {env_file} file found (this is OK if using Heroku Config Vars)")
    
    print(f"🚀 Starting Movie Recommendations API in production mode...")
    print(f"📁 Working directory: {backend_dir}")
    
    # Get port from environment variable (Heroku sets this), default to 8000 for local development
    port = os.getenv("PORT", "8000")
    
    # Gunicorn configuration
    gunicorn_config = {
        "app": "app.main:app",
        "bind": f"0.0.0.0:{port}",
        "workers": 1,
        "worker_class": "uvicorn.workers.UvicornWorker",
        "timeout": 120,
        "keepalive": 5,
        "max_requests": 100,
        "max_requests_jitter": 20,
        "preload_app": True,
        "access_logfile": "-",
        "error_logfile": "-",
    }
    
    # Build the Gunicorn command
    cmd = ["python", "-m", "gunicorn"]
    
    for key, value in gunicorn_config.items():
        cmd.append(f"--{key.replace('_', '-')}")
        cmd.append(str(value))
    
    cmd.append("app.main:app")
    
    print(f"🔧 Port: {port}")
    print(f"🔧 Command: {' '.join(cmd)}")
    print("=" * 50)
    
    try:
        # Start the server
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Gunicorn not found. Please install it with: pip install gunicorn uvicorn")
        sys.exit(1)

if __name__ == "__main__":
    main()
