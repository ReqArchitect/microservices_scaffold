# Application Layer Service

A microservice for managing ArchiMate 3.2 Application Layer concepts (ApplicationComponent, ApplicationCollaboration, ApplicationInterface, ApplicationFunction, ApplicationInteraction, ApplicationService, DataObject) in ReqArchitect.

## Features
- CRUD APIs for all application layer concepts
- JWT authentication and multi-tenancy
- SQLAlchemy models
- OpenAPI (Swagger) documentation (to be added)
- Modular Flask app structure
- Docker support
- Unit/integration test skeletons with pytest

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
- `/api/application_components` CRUD for ApplicationComponent
- `/api/application_collaborations` CRUD for ApplicationCollaboration
- `/api/application_interfaces` CRUD for ApplicationInterface
- `/api/application_functions` CRUD for ApplicationFunction
- `/api/application_interactions` CRUD for ApplicationInteraction
- `/api/application_services` CRUD for ApplicationService
- `/api/data_objects` CRUD for DataObject

## Testing
- Unit and integration tests in `tests/`
- Run with:
   ```powershell
   pytest
   ```

## License
MIT
