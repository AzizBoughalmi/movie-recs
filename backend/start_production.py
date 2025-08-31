#!/usr/bin/env python3
"""
Production startup script for the Movie Recommendations API
This script configures and starts the FastAPI application using Gunicorn for production deployment.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Start the FastAPI application with Gunicorn in production mode."""
    
    # Ensure we're in the backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # Load environment variables from .env.production if it exists
    env_file = ".env.production" if os.path.exists(".env.production") else ".env"
    
    print(f"🚀 Starting Movie Recommendations API in production mode...")
    print(f"📁 Working directory: {backend_dir}")
    print(f"🔧 Environment file: {env_file}")
    
    # Gunicorn configuration
    gunicorn_config = {
        "app": "app.main:app",  # FastAPI app location
        "host": "0.0.0.0",      # Listen on all interfaces
        "port": "8000",         # Default port
        "workers": "4",         # Number of worker processes
        "worker_class": "uvicorn.workers.UvicornWorker",  # Use Uvicorn workers for async support
        "timeout": "120",       # Worker timeout
        "keepalive": "5",       # Keep-alive timeout
        "max_requests": "1000", # Restart workers after handling this many requests
        "max_requests_jitter": "100",  # Add randomness to max_requests
        "preload_app": True,    # Preload the application for better performance
        "access_logfile": "-",  # Log to stdout
        "error_logfile": "-",   # Log errors to stderr
    }
    
    # Build the Gunicorn command
    cmd = ["python", "-m", "gunicorn"]
    
    for key, value in gunicorn_config.items():
        if key == "app":
            cmd.append(value)
        else:
            cmd.extend([f"--{key.replace('_', '-')}", value])
    
    # Add environment file if specified
    if env_file != ".env":
        cmd.extend(["--env", f"DOTENV_PATH={env_file}"])
    
    print(f"🔧 Command: {' '.join(cmd)}")
    print("=" * 50)
    
    try:
        # Start the server
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Gunicorn not found. Please install it with: pip install gunicorn")
        sys.exit(1)

if __name__ == "__main__":
    main()
