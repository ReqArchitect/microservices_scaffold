# Strategy Service

A microservice for managing Capabilities and Courses of Action, forming the core of the transformation pipeline in ReqArchitect.

## Features
- CRUD APIs for Capability and CourseOfAction entities
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
- `/api/capabilities` CRUD for Capability
- `/api/courses_of_action` CRUD for CourseOfAction

## Testing

### Unit & Integration Tests
- Each service contains its own `tests/` folder for unit and integration tests.
- Run from the service directory:
   ```powershell
   pytest
   ```

### End-to-End (E2E) Tests
- Cross-service integration tests are in the project root `e2e_tests/` folder.
- To run E2E tests locally:
   1. Start all required services (see Docker Compose below).
   2. In project root:
      ```powershell
      pytest e2e_tests/
      ```
- E2E tests require all services and databases to be running.

### Docker Compose (Recommended for E2E)
- Use the provided `docker-compose.yml` to spin up all services, databases, and run E2E tests:
   ```powershell
   docker compose up --build
   ```
- This ensures a clean, production-like environment for full-stack testing.

### Best Practices
- Keep unit/integration tests in each service's `tests/` folder.
- Keep E2E/cross-service tests in `e2e_tests/` at the project root.
- Use fixtures to clean up test data and ensure repeatability.
- Automate all tests in CI/CD pipelines.
- Document all test procedures and troubleshooting tips.

## License
MIT

