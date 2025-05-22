"""
Main entry point for the AI Orchestrator Service
"""
import os
from app import create_app

app = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    port = int(os.environ.get('SERVICE_PORT', 5100))
    app.run(host='0.0.0.0', port=port)
