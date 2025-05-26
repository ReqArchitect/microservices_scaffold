# Scripts Directory

This directory contains all utility and automation scripts for the monorepo.

- `Makefile`: Common dev/ops tasks (build, test, lint, migrate, etc)
- `run_service.py`: Entrypoint for running services
- `run_chaos_tests.py`: Chaos testing runner
- `run_code_quality_checks.py`: Linting and code quality checks
- `install_all_requirements.py`: Install all dependencies
- `update_docker_compose.py`: Update docker-compose file(s)
- `setup_code_quality.py`: Setup code quality tools
- `setup_local_env.py`: Setup local development environment

## Test Data Scripts
- `seed_test_data.py`: Seeds test data for all services
- `cleanup_test_data.py`: Cleans up test data after tests

## Contract and Chaos Testing
- `run_contract_tests.py`: Runs contract tests using Schemathesis/Dredd
- `run_chaos_tests.py`: Runs chaos/fault injection tests

All scripts are invoked from this directory. See each script for usage details. 