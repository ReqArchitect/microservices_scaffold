# Monorepo Architecture & Structure

## Root Structure

- `docs/`: All documentation, guides, API specs, and Dockerfiles for docs/testing
- `scripts/`: All utility scripts, Makefile, and automation
- `config/`: All config files (linter, pre-commit, pyproject, etc)
- `requirements/`: All requirements files (prod/dev)
- `tests/`: All root-level test scripts
- `docker-compose.yml`: The only compose file at root (uses YAML anchors for DRY)
- `common_utils/`: Shared code for all services
- `<service_name>/`: All microservices (user_service, auth_service, etc)

## Best Practices

- DRY: No duplicate requirements, config, or scripts
- All dependencies are pinned and managed centrally
- All documentation is in one place
- All config is in one place
- All scripts are in one place
- Only one docker-compose.yml at root
- README.md is in docs/ (symlinked to root if needed)

## How to Add New Services

1. Create a new `<service_name>/` directory
2. Add service code, but use shared `common_utils/` and root requirements
3. Add any new requirements to `requirements/requirements.txt` and re-run install
4. Add service to `docker-compose.yml` using YAML anchors for DRY

## How to Add New Scripts/Config/Docs

- Add scripts to `scripts/`
- Add config to `config/`
- Add docs to `docs/`

## How to Run/Build

- Use `scripts/Makefile` for all common tasks
- Use `docker-compose.yml` for orchestration

---

This structure is designed for maintainability, scalability, and production-readiness. 