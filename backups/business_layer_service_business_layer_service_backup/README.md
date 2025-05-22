# Business Layer Service

A microservice for managing Business Actors, Business Processes, Goals, and Objectives, forming the business modeling layer in ReqArchitect.

## Features
- CRUD APIs for BusinessActor, BusinessProcess, Goal, and Objective entities
- JWT authentication
- SQLAlchemy models
- OpenAPI (Swagger) documentation
- Modular Flask app structure
- Docker support
- Unit test skeletons with pytest

## Project Structure
- app/
  - __init__.py
  - models.py
  - routes.py
  - auth.py
  - utils/
  - swagger.py
- config.py
- requirements.txt
- Dockerfile
- migrations/
- tests/
- README.md

## Setup
1. Create and activate a virtual environment in this directory:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Set environment variables (see `config.py`) or use a `.env` file at the project root (recommended).
4. Run database migrations
5. Start the service:
   ```powershell
   python main.py
   ```

## API
- `/api/business_actors` CRUD for BusinessActor
- `/api/business_processes` CRUD for BusinessProcess
- `/api/goals` CRUD for Goal
- `/api/objectives` CRUD for Objective

## License
MIT
